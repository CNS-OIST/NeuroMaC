#!/bin/bash

# uncomment next line for interactive checking of generated output
PYTHON="ipython --pylab -i"
# non-interactive shell. Check results afterwards
PYTHON="python"

# Motor neuron
# Generates a L5 pyramidal neuron morphology as in Figure 4 of Torben-Nielsen, B.,
#  & De Schutter, E. (2014) Context-aware modeling of neuronal morphologies. Frontiers in
#  Neuroanatomy, 8, 92. http://doi.org/10.3389/fnana.2014.00092/abstract
# Movie commented by default as it takes a long time to generate
time PYTHONPATH=pyramidal_neuron/:$PYTHONPATH python ../Admin.py 4 pyramidal_neuron/pyramid_single.cfg
python ../scripts/generate_SWC_data.py pyramidal_neuron/pyramid_single.cfg pyramidal_neuron/L5_pyramidal_neuron.db
#python ../scripts/helper_generate_movie.py pyramidal_neuron/pyramid_single.cfg pyramidal_neuron/L5_pyramidal_neuron.db
$PYTHON ../scripts/generate_wire_plot.py pyramidal_neuron/pyramid_single.cfg pyramidal_neuron/L5_pyramidal_neuron.db
$PYTHON ../scripts/generate_radii_plot.py pyramidal_neuron/pyramid_single.cfg pyramidal_neuron/L5_pyramidal_neuron.db
