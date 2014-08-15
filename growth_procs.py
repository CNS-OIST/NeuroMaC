import time,copy
import numpy as np

compute_exp_decay_factor = lambda i,d,x : i*np.exp(-d*x)

def unit_sample_on_sphere() :
    xs = np.random.normal(size=3)
    denominator = np.sqrt(np.sum(xs**2))
    origin = np.array([0,0,0])
    to = [x / denominator for x in xs]
    return np.array(to)

def get_entity(entity_name,constellation) :
    entities = []
    for key in constellation.keys() :
        if key.startswith(entity_name):
            entities = entities + constellation[key]
    return entities

def get_eigen_entity(front,constellation,ancestry_limit=25,common_ancestry_limit=10):
    entity_name = front.entity_name
    entities = []
    for key in constellation.keys() :
        if key.startswith(entity_name):
            entities = entities + constellation[key]
    entities = map(tuple,entities)
    #print "entities: ", entities

    """Now prune the list of entities. Remove:
    1. ancestors less than <ancestry_limit> micron away
    2. fronts that have common ancestors less then <common_ancestry_limit> micron away (this happens at bifurcations)
    
    construct a list of positions, that will be removed from the entities list
    """
    len_before = len(entities)
    to_be_removed = []
    to_be_removed.append(front.xyz) # no cue from yourself

    print "self as tuple:", tuple(front.xyz)
    
    entities.remove(tuple(front.xyz))
    path_L = 0
    c_front = front
    while path_L < ancestry_limit:
        parent = c_front.parent
        if parent == None:
            break
        path_L = path_L + np.sqrt(np.sum((c_front.xyz-parent.xyz)**2))
        to_be_removed.append(parent.xyz)
        c_front= parent
        entities.remove(tuple(parent.xyz))
    len_after = len(entities)
    print "len(entities), before=%i, after=%i" % (len_before,len_after)
    entities = map(np.array,entities)
    return entities
    

def prepare_next_front(front,new_pos,radius_factor=None,set_radius=None,add_order=False) :
    new_front = copy.deepcopy(front)
    new_front.parent = front
    new_front.xyz = new_pos
    if not radius_factor == None:
        #print "front, radius_factor, front.radius:",radius_factor," * radius:",front.radius," = ", (front.radius*radius_factor)
        #time.sleep(1)
        new_front.radius = front.radius*radius_factor
    if not set_radius == None:
        new_front.radius= set_radius
    new_front.path_length = new_front.path_length+np.sqrt(np.sum((front.xyz-new_front.xyz)**2))
    if add_order :
        new_front.order = front.order + 1
    return new_front        

def normalize_length(vec,norm_L) :
    if vec == None:
        return [0,0,0]
    return vec / np.sqrt(np.sum((vec)**2)) * norm_L

def direction_to(front,list_of_others,what="average") :
    """ Determines the vector towards *some other entities*. 
    """
    if len(list_of_others) == 0 :
        # shouldn't this be array([0,0,0])??? No items, null vector
        #return np.array([0,0,0])
        return None # handle the error somewhere else
    pos = front.xyz
    vecs = []
    smallest_vec = np.array([100000000,100000000,100000000])
    for loc in list_of_others :
        vec = loc-pos#pos-loc
        vecs.append(vec)
        # THIS SHOULD BE MEMORIZED / TABULATED ++++++++++++++++++++ <-----
        if np.sqrt(np.sum((loc-pos)**2)) < np.sqrt(np.sum((smallest_vec)**2)) :
            smallest_vec = vec
    if what == "nearest" :
        return smallest_vec
    else :
        return vecs

def gradient_to(front,list_of_others,strength,decay_factor,what="average",cutoff=0.01) :
    """ Determines the vector towards *some other entities*. 
    """
    #all_vecs = direction_to(front,list_of_others,what=what)
    nearest_vec = np.array([100000000,100000000,100000000])
    if what == "nearest" :
        nearest_vec = direction_to(front,list_of_others,what=what)
        L = np.sqrt(sum((nearest_vec)**2))
        decay = compute_exp_decay_factor(strength,\
                                         decay_factor,\
                                         L)
        print "self_rep, L=%.2f, decay=%.2f " % (L,decay)
        nearest_vec = (nearest_vec/ L * decay)
        L = np.sqrt(sum((nearest_vec)**2))
        print "self_rep, L=%.2f, decay=%.2f, cutoff=%.2f" % (L,decay,cutoff)
        if L < cutoff:
            print "return [0,0,0]"
            return np.array([0,0,0])
        else:
            return nearest_vec        
        
    
# to be replaced
def compute_soma_rep_vec(front,strength=1.0,decay=1.0) :
    """ Compute the respulsive vector directed away from the soma\
    given a provided reference position. The resultant vector is
    AB, with A=[0,0,0] and B the returned array

    Parameters
    ----------

    Returns
    -------
    """
    if np.all(front.soma_pos == front.xyz) :
        vec_from_soma = np.array([0.000001,0.0,0.0])
        print "################################### soma == front"
        import time
        time.sleep(2)
    else :
        vec_from_soma = front.xyz - front.soma_pos # move to origin (of coordinate system)
    L = np.sqrt(sum(vec_from_soma**2))
    decay = compute_exp_decay_factor(strength,decay,L)
    print "soma_pos=%s,f.xyz: %s,L=%.2f,soma decay=%.2f " % (str(front.soma_pos),str(front.xyz),L,decay)
    return (vec_from_soma)/ L * decay
