#!/bin/bash

# uncomment next line for interactive checking of generated output
PYTHON="ipython2 --pylab -i"
# non-interactive shell. Check results afterwards
PYTHON="python2.7"

# Straight to pia: one front runs straight to the pia.
# The pia is a point-cloud, see cfg file and online documentation
time PYTHONPATH=straight_to_pia/:$PYTHONPATH $PYTHON ../Admin.py 4 straight_to_pia/straight.cfg
$PYTHON ../scripts/generate_SWC_data.py straight_to_pia/straight.cfg straight_to_pia/straight.db
$PYTHON ../scripts/helper_generate_movie.py straight_to_pia/straight.cfg straight_to_pia/straight.db
$PYTHON ../scripts/generate_wire_plot.py straight_to_pia/straight.cfg straight_to_pia/straight.db
$PYTHON ../scripts/generate_radii_plot.py straight_to_pia/straight.cfg straight_to_pia/straight.db
