#!/bin/bash

# uncomment next line for interactive checking of generated output
PYTHON="ipython2 --pylab -i"
# non-interactive shell. Check results afterwards
PYTHON="python2.7"

# Example of built-in structural-conflict resolution. 
# Four neurites grow straight apired into two planes. NeuroMaC
# does not allow intersections and will try to resolve the intersection.
# If no resolution is found within the specified number of `avoidance_attempts`,
# the neurite is terminated
time PYTHONPATH=intersection/:$PYTHONPATH python ../Admin.py 1 intersection/intersection.cfg 
python ../scripts/generate_SWC_data.py intersection/intersection.cfg intersection/intersection.db
python ../scripts/helper_generate_movie.py intersection/intersection.cfg intersection/intersection.db
$PYTHON ../scripts/generate_wire_plot.py intersection/intersection.cfg intersection/intersection.db
$PYTHON ../scripts/generate_radii_plot.py intersection/intersection.cfg intersection/intersection.db
