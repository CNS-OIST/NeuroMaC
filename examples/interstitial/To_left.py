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

    if hasattr(front,"side_branch"):
        pass
    else:
        front.side_branch = False
        print "HAS NO SIDE_BRANCH VAR"
        
    if interstitial:
        # this is an interstitial branch
        print "To_left:: INTERSTITIAL TAG"
        new_pos =front.xyz + 3*unit_sample_on_sphere()
        new_front = prepare_next_front(front,new_pos,set_radius=2.0) # 2 and it stops
        new_front.side_branch = True
        return [new_front]
    
    if front.side_branch:
        # grow from main branch
        new_pos =front.xyz + 3*unit_sample_on_sphere()
        dir = -1 * direction_to(front,[front.branch_xyz],what="nearest")
        new_pos = front.xyz + unit_sample_on_sphere() + normalize_length(dir,3.0)
        
        #others_dir = direction_to(front,get_other_entity(front,constellation),what="nearest")
        #new_pos = front.xyz + normalize_length(dir,3)+ unit_sample_on_sphere() +others_dir*2.0
        
        new_front = prepare_next_front(front,new_pos,set_radius=2.0) # 2 and it stops
        return [new_front]
    else:
        new_pos =front.xyz + np.array([L_NORM,0,2.0])
        new_front = prepare_next_front(front,new_pos,set_radius=2.0) # 2 and it stops

        if front.path_length > 10 and np.random.random() < 0.1:
            print "extending front: TAGGING AS INTERSTITIAL"
            # tag as potentially interstitial
            new_front.interstitial = True
            new_front.interstitial_prob = 1.0
            new_front.interstitial_t_offset = 5 + np.random.random_integers(30)
            new_front.branch_xyz = front.xyz
        return [new_front]
