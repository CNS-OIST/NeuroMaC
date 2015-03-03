#!/bin/bash

# uncomment next line for interactive checking of generated output
PYTHON="ipython2 --pylab -i"
# non-interactive shell. Check results afterwards
PYTHON="python2.7"

# example of interstitial branching: a straight branch grows and afterwards
# interstitial/lateral branches sprot from this main branch
time PYTHONPATH=interstitial/:$PYTHONPATH $PYTHON ../Admin.py 1 interstitial/interstitial.cfg 
$PYTHON ../scripts/generate_SWC_data.py interstitial/interstitial.cfg interstitial/interstitial.db
$PYTHON ../scripts/helper_generate_movie.py interstitial/interstitial.cfg interstitial/interstitial.db
$PYTHON ../scripts/generate_wire_plot.py interstitial/interstitial.cfg interstitial/interstitial.db
$PYTHON ../scripts/generate_radii_plot.py interstitial/interstitial.cfg interstitial/interstitial.db
