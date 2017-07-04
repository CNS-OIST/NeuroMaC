#!/bin/bash

# uncomment next line for interactive checking of generated output
PYTHON="ipython2 --pylab -i"
# non-interactive shell. Check results afterwards
PYTHON="python"

# Many to pia demo
# Multiple branching structure growing towards the pia
# For demonstration purposes, putative synapse locations are recorded 
# between neurites.
# Movie commented by default as it takes a long time to generate
time PYTHONPATH=to_pia/:$PYTHONPATH python ../Admin.py 8 to_pia/many.cfg
python ../scripts/generate_SWC_data.py to_pia/many.cfg to_pia/many.db
# python ../scripts/helper_generate_movie.py to_pia/many.cfg to_pia/many.db
$PYTHON ../scripts/generate_wire_plot.py to_pia/many.cfg to_pia/many.db to_pia/many_syn_locs.db
$PYTHON ../scripts/generate_radii_plot.py to_pia/many.cfg to_pia/many.db
