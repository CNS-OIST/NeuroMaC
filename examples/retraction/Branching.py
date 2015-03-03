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

def extend_front(front,seed,constellation,interstitial) :
    if front.update_cycle % 4 == 0 and front.update_cycle != 0:
        # bifurcate
        new_fronts = []
        new_pos =front.xyz + np.array([(20-front.update_cycle),0,3])
        new_front = prepare_next_front(front,new_pos,set_radius=2.0)
        new_fronts.append(new_front)

        new_pos =front.xyz + np.array([-(20-front.update_cycle),0,3])
        new_front = prepare_next_front(front,new_pos,set_radius=2.0)
        new_fronts.append(new_front)

        return new_fronts
    else:
        # grow straight
        new_pos =front.xyz + np.array([0,0,5])
        new_front = prepare_next_front(front,new_pos,set_radius=2.0)
        return [new_front]
