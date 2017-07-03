import copy,time
import random
import numpy as np

from growth_procs import unit_sample_on_sphere,\
     direction_to,\
     gradient_to,\
     normalize_length,\
     get_entity,\
     get_eigen_entity,\
     prepare_next_front

L_NORM=7*0.7
L_MAIN=20*0.7

APICAL_NORM=10*0.7
APICAL_MAIN=10*0.7

MIN_AMP_ANGLE = 15
MAX_ANGLE_ATTEMPTS = 8

def extend_front(front,seed,constellation):
    if front.order == 0:
        new_fronts = []
        apical_front = create_apical_branch(front,constellation)
        basal_fronts = create_basal_branches(front,constellation)
        new_fronts.append(apical_front)
        new_fronts.extend(basal_fronts)
        return new_fronts
    elif front.swc_type==3:
        if front.update_cycle <= np.random.randint(27,40):
            return extend_basal_front(front,constellation)
        else:
            return []
    elif front.swc_type >= 4:# ==4:
        if front.update_cycle <= 1000: # was 90
            return extend_apical_front(front,constellation)
        else:
            return []

def create_apical_branch(front,constellation):
    pia = get_entity("pia",constellation)
    dir_to_pia = direction_to(front,pia,what="nearest")
    try:
        new_dir = normalize_length(dir_to_pia,3.0)
    except Exception:
        new_dir = np.array([0,0,0.1])
    new_pos = front.xyz + normalize_length(new_dir,APICAL_NORM)
    new_front = prepare_next_front(front,new_pos,set_radius=1.0,add_order=True)
    # categories for later processing
    new_front.oblique = False
    new_front.tufted = False
    new_front.swc_type=4

    # OLD: with incorrect aspect ratio pics
    # new_front.repulsion_l1 = 1.0+3*np.random.random()
    # new_front.repulsion_l2 = 0.5+1.0*np.random.random()
    # new_front.repulsion_l3 = 0.5 + 2.* np.random.random()

    # to corretc for aspect ratio pics: more repulsion
    new_front.repulsion_l1 = 1.0*np.random.random()
    new_front.repulsion_l2 = .5+1.0*np.random.random()
    new_front.repulsion_l3 = 2.0+2.0*np.random.random()
    
    return new_front

def create_basal_branches(front,constellation):
    new_fronts = []
    for i in range(np.random.randint(5,11)):
        rnd_dir = unit_sample_on_sphere()
        rnd_dir[2] = -1.0*np.abs(rnd_dir[2]) # try to grow "downwards"/deeper
        new_pos = front.xyz + normalize_length(rnd_dir,L_NORM)
        new_front = prepare_next_front(front,new_pos,set_radius=0.3,add_order=True)
        new_front.swc_type=3
        new_front.no_branch = False
        new_fronts.append(new_front)
    return new_fronts

def extend_basal_front(front,constellation):
    bif_prob = 0.78 / (2.0*front.order+1.0) # was2.5 and  0.8
    bif_prob = bif_prob if front.order < 6 else bif_prob /1.8
    bif_prob = 0.0 if front.order>=6 else bif_prob

    if front.order >= 2 and np.random.random() < 0.07: # wa 00.6
        front.no_branch = True

    if np.random.random() > bif_prob or \
            front.no_branch:
        rnd_dir = unit_sample_on_sphere()
        heading = front.xyz - front.parent.xyz
        soma_dir = -1.0 * normalize_length(direction_to(front,[front.soma_pos],what="nearest"),0.8)

        eigen_entities = get_eigen_entity(front,constellation)
        eigen_dir = np.array([0,0,0])
        eigen_dir = -1.0 * gradient_to(front,eigen_entities,5.0/(front.order),0.05,what="nearest",cutoff=0.2)

        new_dir = normalize_length(heading,1.0) + soma_dir + normalize_length(rnd_dir,1.2) + eigen_dir
        new_pos = front.xyz + normalize_length(new_dir,L_NORM)
        new_front = prepare_next_front(front,new_pos,radius_factor=0.98,add_order=False)

        term_prob = 0.015 * front.order if front.order <=6 else 0.3
        if np.random.random() < term_prob :
             return []
        return [new_front]
    else:
        new_fronts = []
        for i in range(2):
            rnd_dir = unit_sample_on_sphere()
            heading = front.xyz - front.parent.xyz
            new_dir = normalize_length(heading,1.5) +rnd_dir
            new_pos = front.xyz + normalize_length(new_dir,L_NORM)
            new_front = prepare_next_front(front,new_pos,radius_factor=0.98,add_order=True)
            new_fronts.append(new_front)
        return new_fronts

def _scale(a,b,v) : return a+ ( (b-a)*v )
_amp = lambda a: np.sqrt(np.sum((a)**2))
_amp_angle = lambda scaled_1,scaled_2: np.arccos(np.dot(scaled_1,scaled_2)/\
                                                 (_amp(scaled_1)*_amp(scaled_2))) / (2*np.pi/360)        
def extend_apical_front(front,constellation):
    pia = get_entity("pia",constellation)
    dir_to_pia = direction_to(front,pia,what="nearest")
    grad_to_pia = gradient_to(front,pia,5.0,0.015,cutoff=0.3,what="nearest")
    if np.sqrt(sum((grad_to_pia)**2)) >= 3.0:
        print "too close to pia!!! +++++++++++++++++++"
        #time.sleep(1)
        return []
    
    if (front.layer == 4 or front.layer == 5) and not front.oblique :
        # make an oblique dendrite with some probability (and extend the main branch)
        oblique_prob = 0.3 if front.layer == 4 else 0.12 # maybe L5 -> 0.0
        if front.order >= 15:
            oblique_prob = 0.0
            
        if np.random.random() < oblique_prob:
            new_fronts = []
            # orthogonal direction to parent branch: HOWTO?
            rnd_dir = unit_sample_on_sphere()
            heading = front.xyz - front.parent.xyz
            new_dir = normalize_length(heading,0.5) + \
                      normalize_length(rnd_dir,1.0)
            new_pos = front.xyz + normalize_length(new_dir,APICAL_NORM)
            new_front = prepare_next_front(front,new_pos,radius_factor=0.98,add_order=True)
            new_front.oblique = True
            #new_front.swc_type=8
            new_front.oblique_start = front # for directional information
            # if front.layer == 4 and np.random.random() < 0.005:
            #     new_front.oblique=False            

            # and extend
            rnd_dir = unit_sample_on_sphere()
            heading = front.xyz - front.parent.xyz
            new_dir = normalize_length(dir_to_pia,1.5) + \
                      normalize_length(heading,0.) + \
                      normalize_length(rnd_dir,.5)
            new_pos = front.xyz + normalize_length(new_dir,APICAL_MAIN)
            new_front2 = prepare_next_front(front,new_pos,radius_factor=0.98,add_order=True)
            #new_front2.swc_type = 4 if front.layer == 5 else 5
            return [new_front,new_front2]                
        else:
            # only extend
            rnd_dir = unit_sample_on_sphere()
            heading = front.xyz - front.parent.xyz
            new_dir = normalize_length(dir_to_pia,1.5) + \
                      normalize_length(heading,0.) + \
                      normalize_length(rnd_dir,.5)
            new_pos = front.xyz + normalize_length(new_dir,APICAL_MAIN)
            new_front = prepare_next_front(front,new_pos,radius_factor=0.98,add_order=False)
            #new_front.swc_type = 4 if front.layer == 5 else 5
            return [new_front]
        
    if front.oblique:
        # extend or terminate the oblique
        if front.path_length - front.oblique_start.path_length > 100 and np.random.random() < 0.1:
            return []
        else:
            rnd_dir = unit_sample_on_sphere()
            
            eigen_entities = get_eigen_entity(front,constellation)
            eigen_dir = np.array([0,0,0])
            # fairly strong self-repulsion, away from the main trunk...
            eigen_dir = -1.5 * gradient_to(front,eigen_entities,5.0,0.03,what="nearest",cutoff=0.2)

            # or away from the trunk, front.oblique_start
            dir_from_trunk = -1.0 *(front.oblique_start.xyz - front.xyz)
            dir_from_trunk = normalize_length(dir_from_trunk,1.0)
            
            heading = front.xyz - front.parent.xyz
            new_dir = normalize_length(heading,1.0) + \
                      normalize_length(rnd_dir,0.5) + \
                      dir_from_trunk
                      #normalize_length(dir_to_pia,0.1)
                      #eigen_dir # + \
                      # normalize_length(dir_to_pia,0.4)
            if front.layer == 3 :
                new_dir = new_dir + -1.0*normalize_length(dir_to_pia,0.5)
            # if front.layer == 5 :
            #     new_dir = new_dir + normalize_length(dir_to_pia,0.5)            
                      
            new_pos = front.xyz + normalize_length(new_dir,APICAL_NORM)
            new_front = prepare_next_front(front,new_pos,radius_factor=0.98,add_order=False)
            #new_front.swc_type=8
            # make "normal, not oblique"
            return [new_front]

    if front.layer >= 3: #== 3:
        # keep track of the order to limit the number of bifurcations in this layer
        if not hasattr(front, 'start_order_L3') and front.layer ==3:
            # this is the first time, store the current order
            front.start_order_L3 = front.order
        
        # bifurcate or extend
        bif_prob = 0.08
        if front.order - front.start_order_L3 >= 3:
            bif_prob = 0
        if np.random.random() < bif_prob:
            #bifurcate
            new_fronts = []
            first_vec = None
            attempts = 0
            for i in range(2):
                rnd_dir = unit_sample_on_sphere()
                heading = front.xyz - front.parent.xyz
                new_dir = normalize_length(dir_to_pia,0.5) + \
                                  normalize_length(heading,0.5) + \
                                  normalize_length(rnd_dir,1.0)
                new_pos = front.xyz + normalize_length(new_dir,APICAL_NORM)

                # make sure the bif amplitude reaches a minimum...
                if first_vec == None:
                    first_vec = normalize_length(new_dir,APICAL_NORM)
                else:
                    angle_amp = _amp_angle(first_vec,normalize_length(new_dir,APICAL_NORM))
                    while angle_amp <= MIN_AMP_ANGLE and attempts <=MAX_ANGLE_ATTEMPTS:
                        attempts = attempts + 1
                        rnd_dir = unit_sample_on_sphere()
                        heading = front.xyz - front.parent.xyz
                        new_dir = normalize_length(dir_to_pia,0.5) + \
                                          normalize_length(heading,0.5) + \
                                          normalize_length(rnd_dir,1.0)
                        new_pos = front.xyz + normalize_length(new_dir,APICAL_NORM)
                        angle_amp = _amp_angle(first_vec,normalize_length(new_dir,APICAL_NORM))                
                    
                new_front = prepare_next_front(front,new_pos,radius_factor=0.98,add_order=True)
                new_front.tufted = True
                # new_front.swc_type = 5
                new_fronts.append(new_front)
            return new_fronts
        else:
            # simply extend
            rnd_dir = unit_sample_on_sphere()

            eigen_entities = get_eigen_entity(front,constellation)
            eigen_dir = np.array([0,0,0])
            eigen_dir = -1.0 * gradient_to(front,eigen_entities,front.repulsion_l3,0.015,what="nearest",cutoff=0.2)
            gradient_from_pia = -1.0 *gradient_to(front,pia,5*0.7,0.01,what="nearest",cutoff=0.2)

            heading = front.xyz - front.parent.xyz
            new_dir = normalize_length(heading,1.0) + \
                      normalize_length(rnd_dir,0.3) + \
                      eigen_dir + \
                      normalize_length(dir_to_pia,1.)+ \
                      gradient_from_pia 

            new_pos = front.xyz + normalize_length(new_dir,APICAL_NORM)
            new_front = prepare_next_front(front,new_pos,radius_factor=0.98,add_order=False)
            # new_front.swc_type = 6

            # some probability to terminate
            if front.layer ==3 and np.random.random() < 0.01 and front.order - front.start_order_L3 >=3:
                return []
            else:
                return [new_front]
            #return [new_front]

    if front.layer == 2:
        # keep track of the order to limit the number of bifurcations in this layer
        if not hasattr(front, 'start_order_L2'):
            # this is the first time, store the current order
            front.start_order_L2 = front.order
        
        # bifurcate or extend
        bif_prob = 0.1
        if front.order - front.start_order_L3 <= 2:
            bif_prob=0.4
    
        rrr = np.random.random()
        if rrr <= 0.5:
            if front.order - front.start_order_L2 >= 3:
                bif_prob = 0
        else:
            if front.order - front.start_order_L2 >= 4:
                bif_prob = 0
            
        if np.random.random() < bif_prob:
            #bifurcate
            new_fronts = []
            first_vec = None
            attempts = 0
            for i in range(2):
                rnd_dir = unit_sample_on_sphere()
                heading = front.xyz - front.parent.xyz
                new_dir = normalize_length(dir_to_pia,0.5) + \
                                  normalize_length(heading,0.5) + \
                                  normalize_length(rnd_dir,1.0)
                new_pos = front.xyz + normalize_length(new_dir,APICAL_NORM)

                # make sure the bif amplitude reaches a minimum...
                if first_vec == None:
                    first_vec = normalize_length(new_dir,APICAL_NORM)
                else:
                    angle_amp = _amp_angle(first_vec,normalize_length(new_dir,APICAL_NORM))
                    while angle_amp <= MIN_AMP_ANGLE and attempts <=MAX_ANGLE_ATTEMPTS:
                        attempts = attempts + 1
                        rnd_dir = unit_sample_on_sphere()
                        heading = front.xyz - front.parent.xyz
                        new_dir = normalize_length(dir_to_pia,0.5) + \
                                          normalize_length(heading,0.5) + \
                                          normalize_length(rnd_dir,1.0)
                        new_pos = front.xyz + normalize_length(new_dir,APICAL_NORM)
                        angle_amp = _amp_angle(first_vec,normalize_length(new_dir,APICAL_NORM))
                
                new_front = prepare_next_front(front,new_pos,radius_factor=0.98,add_order=True)
                new_front.tufted = True
                # new_front.swc_type = 7
                new_fronts.append(new_front)
            return new_fronts
        else:
            # simply extend
            rnd_dir = unit_sample_on_sphere()

            eigen_entities = get_eigen_entity(front,constellation)
            eigen_dir = np.array([0,0,0])
            eigen_dir = -1.0 * gradient_to(front,eigen_entities,front.repulsion_l2,0.015,what="nearest",cutoff=0.2)
            gradient_from_pia = -1.0 *gradient_to(front,pia,4.0*0.7,0.01,what="nearest",cutoff=0.2)

            heading = front.xyz - front.parent.xyz
            new_dir = normalize_length(heading,1.0) + \
                      normalize_length(rnd_dir,0.3) + \
                      eigen_dir + \
                      normalize_length(dir_to_pia,1.)+ \
                      gradient_from_pia 

            new_pos = front.xyz + normalize_length(new_dir,APICAL_NORM)
            new_front = prepare_next_front(front,new_pos,radius_factor=0.98,add_order=False)
            # front.swc_type = 7

            # some probability to terminate
            if np.random.random() < 0.03:#* (front.order - front.start_order_L2):
                return []
            else:
                return [new_front]
        
    if front.layer == 1:
        # keep track of the order to limit the number of bifurcations in this layer
        if not hasattr(front, 'start_order_L1'):
            # this is the first time, store the current order
            front.start_order_L1 = front.order
        
        # bifurcate or extend
        bif_prob = 0.08
        if front.order - front.start_order_L3 <= 4:
            bif_prob=0.3        
        if front.order - front.start_order_L1 >= 1:
            bif_prob = 0
            
        if np.random.random() < bif_prob:
            #bifurcate
            new_fronts = []
            first_vec = None
            attempts = 0
            for i in range(2):
                rnd_dir = unit_sample_on_sphere()
                heading = front.xyz - front.parent.xyz
                new_dir = normalize_length(dir_to_pia,0.5) + \
                                  normalize_length(heading,0.5) + \
                                  normalize_length(rnd_dir,1.0)
                new_pos = front.xyz + normalize_length(new_dir,APICAL_NORM)

                # make sure the bif amplitude reaches a minimum...
                if first_vec == None:
                    print "first_vec == None, new_dir: ", new_dir
                    first_vec = normalize_length(new_dir,APICAL_NORM)
                else:
                    print "first_vec: ", first_vec, " , other: ", normalize_length(new_dir,APICAL_NORM)
                    angle_amp = _amp_angle(first_vec,normalize_length(new_dir,APICAL_NORM))
                    while angle_amp <= MIN_AMP_ANGLE and attempts <=MAX_ANGLE_ATTEMPTS:
                        attempts = attempts + 1
                        rnd_dir = unit_sample_on_sphere()
                        heading = front.xyz - front.parent.xyz
                        new_dir = normalize_length(dir_to_pia,0.5) + \
                                          normalize_length(heading,0.5) + \
                                          normalize_length(rnd_dir,1.0)
                        new_pos = front.xyz + normalize_length(new_dir,APICAL_NORM)
                        angle_amp = _amp_angle(first_vec,normalize_length(new_dir,APICAL_NORM))
                        print "angle_amp=", angle_amp, ", attemps: ", attempts
                
                new_front = prepare_next_front(front,new_pos,radius_factor=0.98,add_order=True)
                new_front.tufted = True
                #new_front.swc_type = 8
                new_fronts.append(new_front)
            return new_fronts
        else:
            # simply extend
            rnd_dir = unit_sample_on_sphere()

            eigen_entities = get_eigen_entity(front,constellation)
            eigen_dir = np.array([0,0,0])
            eigen_dir = -1.0 * gradient_to(front,eigen_entities,front.repulsion_l1,0.015,what="nearest",cutoff=0.2)
            gradient_from_pia = 0 *gradient_to(front,pia,3.0*0.7,0.01,what="nearest",cutoff=0.2) # 2014-05-12

            heading = front.xyz - front.parent.xyz
            new_dir = normalize_length(heading,1.0) + \
                      normalize_length(rnd_dir,0.3) + \
                      eigen_dir + \
                      normalize_length(dir_to_pia,1.)+ \
                      gradient_from_pia 

            new_pos = front.xyz + normalize_length(new_dir,APICAL_NORM)
            new_front = prepare_next_front(front,new_pos,radius_factor=0.98,add_order=False)
            #new_front.swc_type = 8

            if np.random.random() < 0.06:
                return []
            else:
                return [new_front]                            
            return [new_front]
