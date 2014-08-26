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
