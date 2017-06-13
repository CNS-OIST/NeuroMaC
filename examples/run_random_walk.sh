#!/bin/bash

# uncomment next line for interactive checking of generated output
PYTHON="ipython --pylab -i"
# non-interactive shell. Check results afterwards
PYTHON="python"

# Random walk
# Not truly a rondom walk as the generated structure will terminate \
# when a structural overlap occurs. Detecting and avoiding a \
# structual ooverlap is a main feature of NeuroMaC
time PYTHONPATH=random_walk/:$PYTHONPATH python ../Admin.py 1 random_walk/random_walk.cfg 
python ../scripts/generate_SWC_data.py random_walk/random_walk.cfg random_walk/random_walk.db
python ../scripts/helper_generate_movie.py random_walk/random_walk.cfg random_walk/random_walk.db
$PYTHON ../scripts/generate_wire_plot.py random_walk/random_walk.cfg random_walk/random_walk.db
$PYTHON ../scripts/generate_radii_plot.py random_walk/random_walk.cfg random_walk/random_walk.db
