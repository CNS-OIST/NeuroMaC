"""
max subvolumes=999999 (SV addresses are: %06d)
"""

import zmq
import sys
import os
import time
import sqlite3
from ConfigParser import SafeConfigParser # For use with Python 2.7
import numpy as np
import cPickle as pickle

from front import Front
import btmorph

from multiprocessing import Process

import inspect
def _me(bool) :
    if(bool) :
        print '%s \t Call -> ::%s' % (inspect.stack()[1][1], inspect.stack()[1][3])
    else :
        pass

def print_with_rank(message) :
    print '%s \t \t%s' % (inspect.stack()[1][1], message)

class Admin_Agent(object) :
    """
    Admin agent: initializes the simulation, decomposes space and
    assigns space to Subvolume agents. Growth cones are also initialized
    here and distributed to the Subvolumes corresponding to the location
    of the growth cones.

    Modelled as conceptually close to biology but great in load balancing...
    """
    def __init__(self,total_processors,cfg_file="test_config.cfg") :
        self.cfg_file = cfg_file
        self.parser = SafeConfigParser()
        self.parser.read(cfg_file)
        np.random.seed(self.parser.getint("system","seed"))
        if self.parser.has_option("system","recursion_limit"):
            sys.setrecursionlimit(self.parser.getint("system","recursion_limit"))
        self.substrate={}
        # a few variable should be global
        self.total_processors = total_processors # until I find a better way
        self.processor_ids = range(1,self.total_processors) # start from 1: skip the Admin
        self.summarized_constellations = {} # store summarized constellations based on their self.num / proc id
        self.non_swc_trees = {} # construct trees from extending Fronts
        # set up communication links for the Admin
        self._initialize_communication_links()
        self._setup_DBs()
        ret = self._initialize_SVs()
        time.sleep(1) # sleep a second: make sure al SVs are initialized (all messages processed)
        if ret < 0 :
            self._destruction()
            return # and break out
        ret = self._initialize_GE_beta()
        if ret < 0 :
            self._destruction()
            return
        
        # and continue with the real deal if we haven't been kicked out yet
        self.main_loop()
        
        self._destruction()

    def _initialize_communication_links(self) :
        """ Set up the communication links to and from the Admin
        """
        self.context = zmq.Context()

        """ Initialize socket to receive incoming messages. Incoming messages \
        are queued "fair" according to 0MQ...
        """
        self.socket_pull = self.context.socket(zmq.PULL)
        self.socket_pull.bind("tcp://*:%s" % self.parser.getint("system","pull_port"))

        # SETUP PROXY: to communicate through a proxy; all-to-all
        self.psub = self.context.socket(zmq.SUB)
        self.psub.connect("tcp://localhost:%s" % self.parser.getint("system","proxy_pub_port")  )
        self.psub.setsockopt(zmq.SUBSCRIBE, "Admin")        
        self.ppub = self.context.socket(zmq.PUB)
        self.ppub.connect("tcp://localhost:%s" % self.parser.getint("system","proxy_sub_port"))        

        self.poller = zmq.Poller()
        self.poller.register(self.psub, zmq.POLLIN)

        registered = 0
        while registered < len(self.processor_ids) :
            msg = self.socket_pull.recv()
            print_with_rank(str(msg))
            registered = registered + 1
        print "all Subvolumes registered. Proceed!"

    def _setup_DBs(self) :
        self.db_file_name = self.parser.get("system","out_db")
        try :
            os.remove(self.db_file_name)
        except Exception :
            pass
        self.conn = sqlite3.connect(self.db_file_name)
        self.conn.execute('''CREATE TABLE swc_data (id INTEGER PRIMARY KEY AUTOINCREMENT,\
                                            name text,\
                                            swc_type int,\
                                            from_x real, \
                                            from_y real, \
                                            from_z real,\
                                            to_x real,\
                                            to_y real,\
                                            to_z real,\
                                            radius real,\
                                            hash integer,\
                                            proc integer)''')

        # only if this parameter is set in the config file
        if self.parser.has_option("system","syn_db"):
            self.syn_file_name = self.parser.get("system","syn_db")
            try :
                os.remove(self.syn_file_name)
            except Exception :
                pass
            self.syn_conn = sqlite3.connect(self.syn_file_name)
            self.syn_conn.execute('''CREATE TABLE synapses (id INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                pre_syn_entity text,\
                                                pre_x real,\
                                                pre_y real,\
                                                pre_z real,\
                                                post_syn_entity text,\
                                                post_x real,\
                                                post_y real,\
                                                post_z real)''')

                                            
    def _get_substrate_information(self) :
        for option in self.parser.options("substrate") :
            if not option.startswith("dim_") : # then this is an entity
                val = self.parser.get("substrate", option)
                if val.endswith("pkl") :
                    self.substrate[option] = pickle.load(open(val,"r"))
                else :
                    print_with_rank("substrate entity (%s) should be given as name of a pickle file" % option)
        time.sleep(0.0)

    def _get_sub_substrate(self,boundary) :
        sub_substrate = {}
        b0 = np.array(boundary[0])
        b1 = np.array(boundary[1])
        for entity in self.substrate :
            print "checking entity: ", entity, ", boundary: ", boundary

            # 2014-08-08, make all internals sets of fronts.. bit redundant memory wise, but easy for administration
            sub_substrate[entity] = set()
            for ppoint in self.substrate[entity] :
                point = ppoint[0]
                t_front = Front(None,None,point,ppoint[1],0,0)
                sub_substrate[entity].add(t_front)
                #time.sleep(1)
            if len(sub_substrate[entity]) == 0 :
                sub_substrate.pop(entity,None)
        return sub_substrate
    

    def _get_virtual_substrate(self):
        virtual_substrate ={}
        for name,value in self.parser.items("substrate"):
            if name.startswith("virtual"):
                virtual_name = name.split("_")[1]
                print  "Found virtual: ",virtual_name
                virtual_substrate.update({virtual_name:eval(self.parser.get("substrate",name))})

        if virtual_substrate == {}:
            print "No virtual substrates found"
            #time.sleep(5)
        else:
            print "virtual_substrate:\n",virtual_substrate
            #time.sleep(5)
        return virtual_substrate
                                            
    def _initialize_SVs(self) :
        required = ["xa","ya","za"]
        for item in required :
            if not self.parser.has_option("sub_volumes",item) :
                print_with_rank( "%s does not exists in the cfg file" % item)
        xa,ya,za = self.parser.getint("sub_volumes","xa"), \
          self.parser.getint("sub_volumes","ya"), \
          self.parser.getint("sub_volumes","za")

        # CHECK: do I still need this clause???
        if  xa*ya*za > (len(self.processor_ids)) :
            print_with_rank("Not enough processors (%i processors for %i SVs)" \
              % (len(self.processor_ids),xa*ya*za))
            return -1 # fetch in __init__

        substrate = self._get_substrate_information()
            
        dim_xyz = eval(self.parser.get("substrate","dim_xyz"))
        x_space = dim_xyz[0] / xa
        y_space = dim_xyz[1] / ya
        z_space = dim_xyz[2] / za
        self.space_division = {} # per ZMQ processor what part of the Volume they control
        self.assigned_ids = {} # per chunk of Volume, which processor controls it
        count = 0
        for i in range(xa) :
            for j in range(ya) :
                for k in range(za) :
                    x0,y0,z0 = i*x_space,j*y_space,k*z_space
                    x1,y1,z1 = (i+1)*x_space,(j+1)*y_space,(k+1)*z_space
                    self.space_division[i,j,k] = [[x0,y0,z0],[x1,y1,z1]]
                    self.assigned_ids[i,j,k] = self.processor_ids[count]
                    print_with_rank("proc: %i [%i,%i,%i]= %1.f,%1.f,%1.f -> %1.f,%1.f,%1.f" \
                                    % (self.processor_ids[count],i,j,k,x0,y0,z0,x1,y1,z1))
                    count = count + 1

        # for now, pass the global virtual information to each SV (independent of SV boundaries)
        virtual_substrate = self._get_virtual_substrate()
                    
        for key in sorted(self.space_division.keys()) :
            dest = self.assigned_ids[key]
            print_with_rank("key: "+ str(key)+ "type: "+ str(type(key))+ "assigned to "+str(dest))
            boundary = self.space_division[key]
            neighbors = []
            for i in range(key[0]-1, key[0]+2) :
                for j in range(key[1]-1, key[1]+2) :
                    for k in range(key[2]-1, key[2]+2) :
                        new_key = (i,j,k)
                        if new_key in self.space_division and key != new_key :
                            neighbors.append(self.assigned_ids[i,j,k])
            print_with_rank("neighbors of "+str( dest)+  ": "+ str(neighbors))
            """ get part of the substrate contained in this SV, prepare to include in message.
            currently the substrate entities are represented by points
            """
            sub_substrate = self._get_sub_substrate(boundary)

            print_with_rank("sending Init_SV to %06d"%dest )
            message = ("Init_SV",boundary,neighbors,sub_substrate,virtual_substrate)
            self.ppub.send_multipart(["%06d"%dest,pickle.dumps(message)])
            # time.sleep(2)
        return 1 # positive: all is well

    def _initialize_GE_beta(self) :
        cfg_sections = self.parser.sections()
        ship_entity_to_proc = {}
        for i in self.processor_ids :
            ship_entity_to_proc[i]= []
        for name in cfg_sections :
            if name.startswith("cell_type") :
                entity_id = 0
                print_with_rank( "found cell type: %s" % name)
                # retrieve algo to use and how many to deploy
                no_seeds = self.parser.getint(name,"no_seeds")
                algorithm_name = self.parser.get(name,"algorithm")
                """ Sample the soma position of the entity and assign \
                    to the correct processor
                """
                loc = eval(self.parser.get(name,"location"))
                rs =  eval(self.parser.get(name,"soma_radius"))

                for seed in range(no_seeds) :
                    details = {}
                    for option in self.parser.options(name) :
                        details.update({option:self.parser.get(name,option)})
                        
                    soma_xyz = np.array([])
                    for i in range(3): # 3D
                        soma_xyz = np.append(soma_xyz,(loc[1][i]-loc[0][i])*np.random.random()+loc[0][i] )
                        
                    # soma_pos = P3D2(soma_xyz,radius=rs)
                    details["radius"] = rs
                    details["soma_xyz"] = soma_xyz

                    dest = self._which_volume_contains_position(soma_xyz)
                    if dest == -1 :
                        print_with_rank("Could not find subvolume for soma: " + str(soma_xyz))
                        return -1
                    print_with_rank("sampled s%i:%s  (D:%i)" % (seed,str(soma_xyz),dest))
                    
                    entity_name = name + "__" +str(entity_id)
                    details.update({'entity_name':entity_name})
                    ship_entity_to_proc[dest].append(details)
                    entity_id = entity_id + 1

        # print_with_rank("ship_entity_to_proc: " + str(ship_entity_to_proc))

        total_no_entities = 0
        for proc in ship_entity_to_proc.keys() :
            entries = ship_entity_to_proc[proc]
            total_no_entities = total_no_entities + len(ship_entity_to_proc[proc])
            message=("Initialize_GEs",entries)
            # comm.send(message,dest=proc,tag=2)
            self.ppub.send_multipart(["%06d"%proc,pickle.dumps(message)])
            print_with_rank("to %i: %s" % (proc,str(message)))

        # 2015-02-25
        # maybe I can wait here for the retured somata...
        received_somata = 0
        while received_somata < total_no_entities:
            print_with_rank("waiting: received={0} from total {1}".format(received_somata,total_no_entities))
            [address,message] = self.psub.recv_multipart()
            message = pickle.loads(message)
            sender = message[1]
            if message[0] == "Soma_fronts":
                soma_fronts = message[2]
                received_somata = received_somata + len(soma_fronts)
                print_with_rank("waiting [end]: received={0} from total {1}".format(received_somata,total_no_entities))

                for front in soma_fronts:
                    # start a tree with the somata
                    p3d = btmorph.P3D2(front.xyz,front.radius,1) # 1: SWC soma type
                    t_node = btmorph.SNode2(hash(front))
                    t_node.content={'p3d':p3d,'front':front}
                    self.non_swc_trees[front.entity_name]=btmorph.STree2()
                    self.non_swc_trees[front.entity_name].root = t_node
            else:
                print_with_rank("this should not happen, received {0} from {1}".format(sender,message[0]))
            
        return 1 # positive: all is well        
    
    def main_loop(self) :
        """ Perform some update cycles. When the admin publishes an \
        "Update" note, the Subvolumes send their current "my_constellation" \
        and their summarized constellation to the Admin.
        1. wait/gather all the info/constellations from each SV
        2. wait for replies
        3. proceed to next Update cycle
        """
        keep_snapshots = False
        if self.parser.has_option("system","keep_snapshots"):
            keep_snapshots=self.parser.getboolean("system","keep_snapshots")
                    
        for i in range(self.parser.getint("system","no_cycles")) :
            for dest in self.processor_ids :
                message = ("Update",i,self.summarized_constellations)
                self.ppub.send_multipart(["%06d"%dest,pickle.dumps(message)])
            responses = 0
            fronts_to_be_retracted = []
            while responses < len(self.processor_ids) :
                # socks = dict(self.poller.poll())

                # if self.psub in socks and socks[self.psub] == zmq.POLLIN:
                [address,message] = self.psub.recv_multipart()
                message = pickle.loads(message)
                print_with_rank("received message on PULL")
                if message[0] == "Update_OK" :
                    responses = responses + 1
                    sender = int(message[1])
                    changes = message[2]
                    syn_locs = message[3]
                    t_constellation = message[4]
                    
                    # write changes
                    self._temp_to_db(changes,sender)

                    """instead of writing changes, construct tree structure
                    on the fly.
                    Initial tree (root) is created when GES are distributed"""
                    self._expand_tree(changes,sender)
                    
                    # store putative synapse locations
                    if self.parser.has_option("system","syn_db"):
                        self._syn_to_db(syn_locs,sender)
                    # store internally
                    self.summarized_constellations[sender] = t_constellation

                elif message[0] == "Migrate_Front" :
                    self._process_migrate_front(message)
                    time.sleep(0.)
                elif message[0] == "Extra_synapses" :
                    print_with_rank("EXTRA_SYNAPSES")
                    sender = int(message[1])
                    syn_locs = message[2]
                    # store putative synapse locations
                    if self.parser.has_option("system","syn_db"):
                        self._syn_to_db(syn_locs,sender)
                elif message[0] == "Extra_front":
                    sender = int(message[1])
                    extra_front = message[2]
                    # write changes to DB: TODO 2015-03-03
                    self._temp_to_db([(extra_front.parent,[extra_front])],sender)

                    # Update internal tree structure: TODO 2015-03-03
                    self._expand_tree([(extra_front.parent,[extra_front])],sender)
                elif message[0]=="Request_retract":
                    sender=int(message[1])
                    front_to_retract = message[2]
                    retraction_depth=message[3]
                    fronts_to_be_retracted.append((front_to_retract,retraction_depth))
            
            # once all messages are received for one update round, process the retractions
            self._process_retraction_requests(fronts_to_be_retracted)
            if keep_snapshots:
                self._convert_to_SWC_and_write(time_stamp=i)
        # write the DB with the morphologies
        self.conn.commit()

        # write DB with synapses (if specified in the config file)
        if self.parser.has_option("system","syn_db"):
            self.syn_conn.commit()

        # convert and write non_swc_trees
        self._convert_to_SWC_and_write()

    def _process_retraction_requests(self,fronts_to_be_retracted):
        """query the tree structure, find all points/fronts and send
        this list back to *all* SVs. After they perform all updates in
        one cycle, they prune their constellations.
        This way, there is a propagation delay of one update cycle,
        which seems reasonable compared to the slow dynamics
        of retraction in biological systems
        """        
        if len(fronts_to_be_retracted)>0:
            print_with_rank("_process_retraction_requests: {0}".format(fronts_to_be_retracted))

        # removal_depth=0
        # if self.parser.has_option("system","retraction_order"):
        #     removal_depth = self.parser.getint("system","retraction_order")

        part_of_retraction = []
        conn = sqlite3.connect(self.db_file_name)
        cursor = conn.cursor()
        
        for (f,removal_depth) in fronts_to_be_retracted:
            # find front in tree
            retract_node = self.non_swc_trees[f.entity_name].get_node_with_index(hash(f))
            print_with_rank("found retract node: {0},xyz={1}".format(retract_node,retract_node.content['front'].xyz))
            #time.sleep(5)

            """find first node downstream of bifurcation node at order=order-removal_depth
            To avoid pruning the whole tree, the depth of removal should be smaller than
            the order of the node that iniated the retraction
            """
            order_of_node = self.non_swc_trees[f.entity_name].order_of_node(retract_node)+1# not an SWC tree, therefore, +1 (whole stem has order=0)
            path_to_root = self.non_swc_trees[f.entity_name].path_to_root(retract_node)

            #print("[before adjustment] removal_depth={0} (node order={1})".format(removal_depth,order_of_node))

            # adjust removal_depth if neccessary
            if removal_depth>order_of_node:
                removal_depth=order_of_node
                print("[sleep] removal_depth={0} (node order={1})".format(removal_depth,order_of_node))

            print_with_rank("retraction removal_depth={0} (node order={1}) [AFTER adjustment] ".format(removal_depth,order_of_node))
            time.sleep(5)
            
            depth = 0
            visited = []
            highest_node = None
            for node in path_to_root[:-1]:
                #print "checking node: {0}".format(node.content['front'].xyz)
                if self.non_swc_trees[f.entity_name].is_root(node):
                    break
                if len(node.children)==2: # this is a bifurcation point
                    depth = depth+1
                    if depth == removal_depth:
                        break
                # now the bifurcation node is spared and highest_node is the node after the bifurcation.
                # if you want to remove the complete bifurcation (the other subtree mounted
                # at the sibling, place the next 3 lines abouve the previous if-statement
                if not node==self.non_swc_trees[f.entity_name].get_root():
                    visited.append(node)
                    highest_node = node                    
            #print_with_rank("found highest node: {0} (with no. child.: {1})".format(highest_node,len(highest_node.children)))

            # get substree mounted at that identified node
            tree_to_rem = self.non_swc_trees[f.entity_name].get_sub_tree(highest_node)
            #print_with_rank("subtree length: {0}".format(len(tree_to_rem.get_nodes())))
            
            # remove all thus found nodes on the Admin
            self.non_swc_trees[f.entity_name].remove_node(highest_node)

            # also from the DB
            for n_node in tree_to_rem.get_nodes():
                n_front = n_node.content['front']
                self.conn.execute("DELETE FROM swc_data where hash={0}".format(hash(n_front)))
            

            # request the SVs to remvoe the same nodes/points
            message = ("Perform_retraction",tree_to_rem.get_nodes())
            for dest in self.processor_ids :
                self.ppub.send_multipart(["%06d"%dest,pickle.dumps(message)])            

            #time.sleep(3)

        """send msg to all SVs notifying to remove any of the nodes to be retracted
        this can be done blindly: send msg to all and they remove from their
        constellation whatever they can remove
        """

    def _convert_to_SWC_and_write(self,time_stamp=None):
        """ copy the trees and change the indices to increases indices,
        not hash codes
        """
        import copy
        copy_tree = copy.deepcopy(self.non_swc_trees)
        
        for (tree,key) in zip(copy_tree.values(),copy_tree.keys()):
            root = tree.get_root()
            nodes = tree.get_nodes()

            root.index = 1
            # add two segment to comply with NeuroMorpho.org three-point soma
            r_p3d =root.content['p3d']
            r_xyz = r_p3d.xyz
            pos1 = btmorph.P3D2(np.array([r_xyz[0],r_xyz[1]-r_p3d.radius,r_xyz[2]]),radius=r_p3d.radius,type=1)#1 = swc type
            pos2 = btmorph.P3D2(np.array([r_xyz[0],r_xyz[1]-r_p3d.radius,r_xyz[2]]),radius=r_p3d.radius,type=1)#1 = swc type
            sub1 = btmorph.SNode2(2)
            sub1.content={'p3d':pos1}
            sub2 = btmorph.SNode2(3)
            sub2.content={'p3d':pos2}
            tree.add_node_with_parent(sub1,root)
            tree.add_node_with_parent(sub2,root)

            # re-number all other nodes with increasing indices
            index = 4
            for node in nodes:
                if not node==root:
                    node.index = index
                    index = index +1

            # write the SWC compliant tree to a file
            if time_stamp==None:
                file_n = "tree_{0}.swc".format(key)
            else:
                file_n = "tree_{0}_T{1}.swc".format(key,time_stamp)
            tree.write_SWC_tree_to_file(file_n)

    def _temp_to_db(self,changes,sender):#front,c_fronts) :
        for front,c_fronts in changes :
            pos = front.xyz
            conn = sqlite3.connect(self.db_file_name)
            cursor = conn.cursor()
            for c_front in c_fronts :
                cpos = c_front.xyz
                name = c_front.entity_name
                radius = c_front.radius
                swc_type = c_front.swc_type
                values = (None,name,swc_type,pos[0],pos[1],pos[2],cpos[0],cpos[1],cpos[2],radius,hash(c_front),"%06d"%int(sender))
                self.conn.execute("INSERT into swc_data VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",values )
        #self.conn.commit()                        

    def _expand_tree(self,changes,sender):
        """
        Dynamically built a non-swc complianted tree representing the neuronal morphology.
        Initial trees with somata are created when the GEs are distributed
        and confirmed by the SVs
        """
        for front,c_fronts in changes :
            parent_id = hash(front)
            parent_node = self.non_swc_trees[front.entity_name][parent_id]
            for c_front in c_fronts :
                cpos = c_front.xyz
                name = c_front.entity_name
                radius = c_front.radius
                swc_type = c_front.swc_type
                daughter_id = hash(c_front)
                #print_with_rank("parent hash={0}, daughter hash={1}".format(parent_id,daughter_id))

                p3d = btmorph.P3D2(cpos,radius,swc_type) 
                t_node = btmorph.SNode2(daughter_id)
                t_node.content={'p3d':p3d,'front':c_front}
                self.non_swc_trees[front.entity_name].add_node_with_parent(t_node,parent_node)
                del(t_node)
                        
    def _syn_to_db(self,syn_locs,sender):
        for syn_loc in syn_locs:
            # pre_front = syn_loc[0]
            # post_front = syn_loc[1]
            # prp = pre_front.xyz
            # pop = post_front.xyz
            # values = (None,pre_front.entity_name,prp[0],prp[1],prp[2],post_front.entity_name,pop[0],pop[1],pop[2])

            pre_name = syn_loc[0]
            pre_x = syn_loc[1]
            pre_y = syn_loc[2]
            pre_z = syn_loc[3]
            post_name = syn_loc[4]
            post_x = syn_loc[5]
            post_y = syn_loc[6]
            post_z = syn_loc[7]
            
            # values = (None,pre_front.entity_name,prp[0],prp[1],prp[2],post_front.entity_name,pop[0],pop[1],pop[2])
            values = (None,pre_name,pre_x,pre_y,pre_z,post_name,post_x,post_y,post_z)
            
            print "values: ", values
            self.syn_conn.execute("INSERT into synapses VALUES (?,?,?,?,?,?,?,?,?)",values)

        
    def _process_migrate_front(self,message) :
        new_front = message[1]
        parent_front = message[2]
        new_dest = self._which_volume_contains_position(new_front.xyz)
        print_with_rank("******: new_dest %i (for %s)" % (new_dest,str(new_front.entity_name)))
        if new_dest == -1 :
            # this front is dead. outside of space
            return
        message = ("Add_Front",new_front)
        #comm.send(message,dest=new_dest,tag=2)
        self.ppub.send_multipart(["%06d"%new_dest,pickle.dumps(message)]) 

    def _which_volume_contains_position(self,pos) :
        for key in self.space_division :
            sv = self.space_division[key]
            if (pos[0] >= sv[0][0]) and \
               (pos[1] >= sv[0][1]) and \
               (pos[2] >= sv[0][2]) and \
               (pos[0] < sv[1][0]) and \
               (pos[1] < sv[1][1]) and \
               (pos[2] < sv[1][2]) :
               return self.assigned_ids[key]
        return -1 # if not found, return -1. Fetch somewhere else
                            
    def _destruction(self) :
        """ Shut down the system. End all threads and all MPI instances
        """
        _me(True)
        print_with_rank("pickle_msg:"+ pickle.dumps("Done") )
        self.ppub.send_multipart(["All",pickle.dumps("Done")])
        self.context.destroy()

def start_proxy(cfg_file) :
    print "starting proxy"
    parser = SafeConfigParser()
    parser.read(cfg_file)
    try:
        print_with_rank("PROXY really starting <-----")
        context = zmq.Context(1)
        # Socket facing clients
        frontend = context.socket(zmq.SUB)
        frontend.bind("tcp://*:%i" % parser.getint("system","proxy_sub_port"))
        frontend.setsockopt(zmq.SUBSCRIBE, "")
        print_with_rank("PROXY subscribed <-----")
        # Socket facing services
        backend = context.socket(zmq.PUB)
        backend.bind("tcp://*:%i" % parser.getint("system","proxy_pub_port"))
        zmq.device(zmq.FORWARDER, frontend, backend)
        print_with_rank("PROXY forwarded <-----")
        print_with_rank("PROXY up and running <-----")
    except Exception, e:
        print e
        print_with_rank("PROXY encountered an error. PROXY down")
    finally:
        print_with_rank("PROXY finally down")
        frontend.close()
        backend.close()
        context.term()
                    
if __name__=="__main__" :
    """
    Start a simulation. Initialize the proxy for message routing,\
    the admin doing the house hold tasks and thethe Subvolumes \
     holding the developing Fronts
    """
    no = int(sys.argv[1])
    cfg_file = sys.argv[2]
    
    proxy = Process(target=start_proxy,args=(cfg_file,))
    proxy.start()
    time.sleep(1) # can I do this in a smarter way? What for a signal that the proxy is ready?
    
    import Subvolume
    svs = []
    for i in range(1,no+1) :
        p = Process(target=Subvolume.start,args=(i,cfg_file))
        svs.append(p)
        svs[-1].start()
    print "Admin going to start with cfg_file: ", cfg_file
    admin = Admin_Agent(no+1,cfg_file)
    print "Admin is ready"
    time.sleep(0.5)
    print "Switching off proxy"
    proxy.terminate()
    print "Proxy switched off"
    for sv in svs :
        sv.terminate()
    print "Admin done. Terminated."
    sys.exit(0) # don't understand why it doesn't clean properly...
