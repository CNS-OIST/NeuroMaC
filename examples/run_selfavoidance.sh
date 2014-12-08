#!/bin/bash

# uncomment next line for interactive checking of generated output
PYTHON="ipython2 --pylab -i"
# non-interactive shell. Check results afterwards
PYTHON="python2.7"

# Self-avoidance example
time PYTHONPATH=self_avoidance/:$PYTHONPATH $PYTHON ../Admin.py 1 self_avoidance/selfavoidance.cfg 
$PYTHON ../scripts/generate_SWC_data.py self_avoidance/selfavoidance.cfg self_avoidance/selfavoidance.db
$PYTHON ../scripts/helper_generate_movie.py self_avoidance/selfavoidance.cfg self_avoidance/selfavoidance.db
$PYTHON ../scripts/generate_wire_plot.py self_avoidance/selfavoidance.cfg self_avoidance/selfavoidance.db
$PYTHON ../scripts/generate_radii_plot.py self_avoidance/selfavoidance.cfg self_avoidance/selfavoidance.db
