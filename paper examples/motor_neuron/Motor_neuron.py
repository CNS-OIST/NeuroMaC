import copy,time
import random
import numpy as np

from growth_procs import unit_sample_on_sphere,\
     direction_to,\
     gradient_to,\
     normalize_length,\
     get_entity,\
     prepare_next_front

L_NORM=40 # fixed-size elongations

def extend_front(front,seed,constellation):
    if front.order==0: # this is the soma
        new_fronts = []
        for i in range(np.random.randint(8,17)):
            rnd_dir = unit_sample_on_sphere()
            new_pos = front.xyz + normalize_length(rnd_dir,L_NORM)
            new_front = prepare_next_front(front,new_pos,set_radius=8.0,add_order=True)
            new_front.swc_type=2
            new_fronts.append(new_front)
        return new_fronts
    else:
        # follow a simple branching rule in all other cases
        bif_prob = 0.6 / (front.order*2.5)
        if front.order > 5 :
            bif_prob = 0.03
        
        if np.random.random() > bif_prob: # continue a front
            # random component
            rnd_dir = unit_sample_on_sphere()
            # unit vector of current heading
            heading = front.xyz - front.parent.xyz
            # soma-tropism, sample direction away from the soma
            soma_dir = -1.0 * normalize_length(direction_to(front,[front.soma_pos],what="nearest"),0.4)
            # combine all infliences on the new direction of growth
            new_dir = normalize_length(heading,1.0) + soma_dir + rnd_dir
            new_pos = front.xyz + normalize_length(new_dir,L_NORM)
            if front.radius <= 0.3 :
                new_front = prepare_next_front(front,new_pos,set_radius=0.3,add_order=False)
            else:
                new_front = prepare_next_front(front,new_pos,radius_factor=0.9,add_order=False)
            # stop growth
            if np.random.random() < 0.06 and front.path_length >= 600 :
                return []
            return [new_front]
        else: # branch a front, generate two child fronts
            new_fronts = []
            for i in range(2):
                rnd_dir = unit_sample_on_sphere()
                heading = front.xyz - front.parent.xyz
                new_dir = normalize_length(heading,1.5) +rnd_dir
                new_pos = front.xyz + normalize_length(new_dir,L_NORM)
                new_front = prepare_next_front(front,new_pos,radius_factor=0.7,add_order=True)
                new_fronts.append(new_front)
            return new_fronts
