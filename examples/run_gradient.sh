#!/bin/bash

# uncomment next line for interactive checking of generated output
PYTHON="ipython2 --pylab -i"
# non-interactive shell. Check results afterwards
PYTHON="python2.7"

# Follow a gradient. Attraction depends on the distance from the attractor.
# The randome xcursions of the neurite become smaller as the neurite approaches
# the attractor
time PYTHONPATH=gradient/:$PYTHONPATH $PYTHON ../Admin.py 1 gradient/to_gradient.cfg 
$PYTHON ../scripts/generate_SWC_data.py gradient/to_gradient.cfg gradient/gradient.db
$PYTHON ../scripts/helper_generate_movie.py gradient/to_gradient.cfg gradient/gradient.db
$PYTHON ../scripts/generate_wire_plot.py gradient/to_gradient.cfg gradient/gradient.db
$PYTHON ../scripts/generate_radii_plot.py gradient/to_gradient.cfg gradient/gradient.db
