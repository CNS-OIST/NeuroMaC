.. _examples:

NeuroMaC examples
=================

This section provides examples highlighting the  key features of NeuroMac \
and illustrate how to use the software suite.

All examples are found in the :code:`examples` directory. Bash shell \
scripts are available to run the models and convert the raw output into \
useful output (such as a SWC-file or figure). Check these shell scripts \
for individual commands.

.. note:: For beginners it is strongly advised not to start a NeuroMac \
   model from scratch but to start with an example and adopt it to \
   meet your needs.

.. _example-random-walk:

Random walk
-----------

*Not truly a random walk.* Rather, several branches grow from the soma, \
start of straight before orientating themselves randomly. \
Consequently, the branches do not grow for long as they will inevitably \
bump into one another. The resultant structural overlaps are detected \
by NeuroMac and cause the branches to terminate.

Run code
~~~~~~~~

Run the example by executing the prepared bash script::
  
   cd examples # Or from wherever you came. From now I assume you're in the examples directory
   ./run_random_walk.py

This script (as well as all further example scripts) will do several things: 

1. Run the model. Running the model generates a SQL database \
   containing all generated structures.
2. Generate one SWC-file of the produced structure
3. Generate a movie of the *development* of the structure.
4. Generate two plots of the produced structure with and without \
   radii, respectively.

The following files will be produced: ::

   random_walk.db # raw SQL database
   cell_type_1__0.swc  # SWC file
   random_walk.mp4 # movie
   random_walk_radii.pdf # plot with radii
   random_walk_wire.pdf  # wire plot


Implementation details
~~~~~~~~~~~~~~~~~~~~~~

The user has to write two files: a configuration file and a file \
containing the growth cones. The configuration file \
(:code:`random_walk/random_walk.cfg`) defines properties of the brain 
volume to simulate as well as which structures to grow in accordance \
to a specified set of rules. Also, the configuration file contains \
some parameters for NeuroMaC itself.

.. todo:: Link to a page detailing the configuration file

Of most interest is the file containing the growth-rules: \
:code:`random_walk/Random_machine.py`

.. literalinclude:: ../../examples/random_walk/Random_machine.py
    :linenos:
    :language: python

In the first three lines several helper functions are imported. These \
come with NeuroMac. For more info on the helper functions click here. \
In short, the :code:`unit_sample_on_sphere` is used to sample a 3D \
vector used as the component for random growth. :code:`normalize_length` \
is used to scale a vector to the desired length while \
:code:`prepare_next_front` is a secure wrapper to extend a front (If \
the work "front" does not ring a bell, please consult the general \
introduction to  NeuroMac first!.)

The actual growth-rule is described in :code:`extend_front(front,seed,constellation)`. \
**Always include this exact method definition** or NeuroMaC will not work!\

In this case two separate rules are included. Two is the unofficial \
default: one rule describes the behaviour at the soma (or any other \
initial point with :code:`front.order==0`) while the other rules \
covers the rest.  Here five initial branches are started. Afterwards \
a front elongates with purely random angles.

- :code:`rnd_dir = unit_sample_on_sphere()`: Get a unit length random\
   3D vector.
- :code:`new_pos = normalize_length(rnd_dir,L_NORM*5)`: Scale a vector \
   to a length of :code:`L_NORM*5`.
- :code:`new_front = prepare_next_front(front,new_pos,set_radius=1.0,add_order=True)`: \
   Create the next front.

.. warning:: :code:`extend_front()` always has to return a list of fronts. \
   If only a single front is returned (as happens for elongations), return a \
   list: :code:`return [new_front]`

.. todo:: Link to the public API and to the NeuroMaC overview



.. _example-attraction:

Attraction between fronts
-------------------------

Basic example illustrating phenomenological attraction between two \
developing neurites. One neurite structure simply grows straight \
while the second neurite is attracted by the first one.

In addition, this example illustrates how to decompose the volume \
through the configuration file.

Configuration file
~~~~~~~~~~~~~~~~~~

Below the configuration file. Note the section :code:`sub_volumes`. \
The volume can be decomposed in a number of rectangles along the \
x, y and z-directions as specified by :code:`xa`, :code:`ya` and \
:code:`za`. Think of this decomposition as making the specified number \
of slices along an axis. The total number of volumes is \
:math:`SV = xa \times ya \times za`. The number :math:`SV` has to be \
given as argument to the Admin.py script as it specifies the number of \
Subvolume agents.

.. todo:: Link to NeuroMaC overview

.. literalinclude:: ../../examples/demo_attraction/demo_attraction.cfg
    :linenos:
    :language: none




Implementation details
~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../examples/demo_attraction/TestF_Left.py
    :linenos:
    :language: python

.. literalinclude:: ../../examples/demo_attraction/TestF_Right.py
    :linenos:
    :language: python

