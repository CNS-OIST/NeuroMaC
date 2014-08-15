import numpy as np

import time # only for testing

class Front(object) :
    def __init__(self,entity_name,algo_name,xyz,radius,\
                 path_length,order) :
        self.entity_name = entity_name
        self.algo_name = algo_name
        self.xyz = xyz
        self.radius = radius
        self.path_length= path_length
        self.order = order
        self.swc_type = 7 # SWC-type field
        self.soma_pos =None
        self.parent = None

    def __str__(self):
        return "Front " + self.entity_name +": " + str(self.xyz)

    def __eq__(self,other):
        if other == None: return False
            
        if not self.entity_name == other.entity_name: return False
        if not self.algo_name == other.algo_name: return False
        if not np.allclose(self.xyz,other.xyz): return False
        if not self.radius == other.radius: return False
        if not self.path_length == other.path_length: return False
        if not self.order == other.order: return False
        if not self.swc_type == other.swc_type: return False
        if other.soma_pos == None:
            if not self.soma_pos == None:
                return False
        else:
            #print "self.soma_pos=", self.soma_pos, ", other.soma_pos=",other.soma_pos
            if not np.allclose(self.soma_pos,other.soma_pos): return False
        if not self.parent == other.parent: return False

        # otherwise, these objects are the same!
        return True

    def __ne__(self,other):
        return not self == other

    def __cmp__(self,other):
        if self.__eq__(other): return 0
        else: return -1

    # quick and dirty way to create a unique hash, needed to work with sets
    def __key(self):
        # WARNING!!! tuple(self.xyz) potentially not correct with rounding errors...
        return (self.entity_name, self.algo_name, tuple(self.xyz),\
                self.radius,self.path_length,self.order,\
                self.swc_type)

    def __hash__(self):
        return hash(self.__key())
    
    def extend_front(self,seed,constellation,virtual_substrate={}) :
        print "extend_Front from Front.py"

        # process the virtual substrate information and set variable in "self"
        for key in virtual_substrate.keys():
            # setattr(x, attr, 'magic')
            for x in virtual_substrate[key].keys():
                rectangle = virtual_substrate[key][x]
                b0 = np.array(rectangle[0])
                b1 = np.array(rectangle[1])
                if np.all(self.xyz>b0) and np.all(self.xyz<b1): # works for rectangle only...
                    setattr(self,key,x)
                    print ">>>> FOUND: ",key," = ",x
                    

        # outsource the real call to extend a front
        globals()[self.algo_name] = __import__(self.algo_name)
        ret = globals()[self.algo_name].extend_front(self,seed,constellation)
        return ret

