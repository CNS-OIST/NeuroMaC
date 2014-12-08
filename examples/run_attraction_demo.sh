#!/bin/bash

# uncomment next line for interactive checking of generated output
PYTHON="ipython2 --pylab -i"
# non-interactive shell. Check results afterwards
PYTHON="python2.7"


# Attraction demo: two structures are grown
# Two subvolumes are used to indicates that environmental cues are not \
# limited to one Subvolume. One branch will grow straight from left to \
# right, one curve starting at the left is attracted by the other \
# curve.
time PYTHONPATH=demo_attraction/:$PYTHONPATH $PYTHON ../Admin.py 2 demo_attraction/demo_attraction.cfg 
$PYTHON ../scripts/generate_SWC_data.py demo_attraction/demo_attraction.cfg demo_attraction/demo_attraction.db
$PYTHON ../scripts/helper_generate_movie.py demo_attraction/demo_attraction.cfg demo_attraction/demo_attraction.db
$PYTHON ../scripts/generate_wire_plot.py demo_attraction/demo_attraction.cfg demo_attraction/demo_attraction.db
$PYTHON ../scripts/generate_radii_plot.py demo_attraction/demo_attraction.cfg demo_attraction/demo_attraction.db
