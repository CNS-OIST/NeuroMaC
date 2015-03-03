#!/bin/bash

# uncomment next line for interactive checking of generated output
PYTHON="ipython2 --pylab -i"
# non-interactive shell. Check results afterwards
PYTHON="python2.7"

# Example of non-builtin avoidance: avoidance is at small spatial scales and done by
# the end user in the front's grwoth rules.
time PYTHONPATH=detailed_avoidance/:$PYTHONPATH $PYTHON ../Admin.py 1 detailed_avoidance/avoidance.cfg 
$PYTHON ../scripts/generate_SWC_data.py detailed_avoidance/avoidance.cfg detailed_avoidance/avoidance.db
$PYTHON ../scripts/generate_wire_plot.py detailed_avoidance/avoidance.cfg detailed_avoidance/avoidance.db
$PYTHON ../scripts/generate_radii_plot.py detailed_avoidance/avoidance.cfg detailed_avoidance/avoidance.db
# $PYTHON ../scripts/helper_generate_movie.py detailed_avoidance/avoidance.cfg detailed_avoidance/avoidance.db
