.. NeuroMaC documentation master file, created by
   sphinx-quickstart2 on Thu Aug 21 17:31:33 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

NeuroMaC's user manual and documentation
========================================

*NeuroMaC is a phenomenological, computational framework to generate \
large numbers of virtual neuronal morphologies (and resultant \
microcircuits) simultaneously according to growth-rules expressed in \
terms of interactions with the environment.*

- **NeuroMaC**: Neuronal Morphologies & Circuits
- **Computational framework**: a suite of software tools built around \
  a central concept
- **Virtual neuronal morphologies**: 3D digital descriptions of \
  neuronal shape (both axons and dendrites)
- **Microcircuits**: Morphologies are generated together in a \
  simulated volume. With the addition of connections rules circuits emerge.
- **Interactions**: Growth-cones branch, terminate and elongate. Each \
  of these steps can be influenced by environmental cues. Most obvious \
  is guidance through repulsion and attraction to simulated cues.
- **Phenomenological**: Neither biochemical pathways nor physics are \
  simulated. As such, growth is purely phenomenological. NeuroMaC is \
  not a simulator of actual neuronal development.

.. note:: Currenly, a prototype of NeuroMaC is implemented in Python. \
This version is a proof-of-principle and nothing beyond that. This \
prototype has many limitations and we are working towards a \
non-prototype version, which should be released in the next year. \
The current prototype code is freely available as well as the models

Contents
========

.. toctree::
   :maxdepth: 3

   neuromac
   docu
   examples
   api
   



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

