import copy,time
import random
import numpy as np

from growth_procs import unit_sample_on_sphere,\
     direction_to,\
     gradient_to,\
     normalize_length,\
     get_entity,\
     get_other_entity,\
     prepare_next_front

L_NORM=4.0
MIN_DISTANCE=3.0

def extend_front(front,seed,constellation,interstitial) :
    if front.update_cycle % 15 == 0 and front.update_cycle > 0:
        # bifurcate, bifurcations points do not retract
        new_fronts = []
        new_pos =front.xyz + np.array([3*(5-front.order),0,3])
        new_front = prepare_next_front(front,new_pos,set_radius=0.5,add_order=True)
        new_fronts.append(new_front)

        new_pos =front.xyz + np.array([-3*(5-front.order),0,3])
        new_front = prepare_next_front(front,new_pos,set_radius=0.5,add_order=True)
        new_fronts.append(new_front)

        return new_fronts
    else:
        # grow straight
        new_pos =front.xyz + np.array([0,0,1])
        new_front = prepare_next_front(front,new_pos,set_radius=0.5)

        # retract? If closer than 3
        other_entities = get_entity("cell_type_line",constellation)
        if len(other_entities)==0:
            return [new_front] # this might happen during the first update_cycle
        else:
            dir_to_entity = direction_to(new_front,other_entities,what="nearest")
            if np.sqrt(sum((dir_to_entity)**2)) < MIN_DISTANCE:
                print "POINT TO RETRACT ***************"
                return -1
            else:
                return [new_front]
