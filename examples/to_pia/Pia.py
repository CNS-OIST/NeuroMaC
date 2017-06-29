import copy,time
import random
import numpy as np

from growth_procs import unit_sample_on_sphere,\
     direction_to,\
     gradient_to,\
     normalize_length,\
     get_entity,\
     prepare_next_front

def extend_front(front,seed,constellation) :
    if front.order == 0 : # soma
        new_fronts = []
        for i in range(2):
            rnd_dir = unit_sample_on_sphere()
            rnd_dir[2] = np.abs(rnd_dir[2])
            new_pos = normalize_length(rnd_dir,25)
            new_pos = front.xyz + new_pos
            new_front = prepare_next_front(front,new_pos,set_radius=3.0,add_order=1)
            new_fronts.append(new_front)
        return new_fronts
    else :
        rnd_dir = unit_sample_on_sphere()
        other_entities = get_entity("pia",constellation)
        #print ("pia entities: ", other_entities)
        dir_to_pia = direction_to(front,other_entities,what="nearest")
        new_pos = front.xyz + normalize_length(dir_to_pia,10)
        new_front = prepare_next_front(front,new_pos,radius_factor=0.5,add_order=False)
        return [new_front]

