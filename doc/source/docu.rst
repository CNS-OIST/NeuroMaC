User manual
===========

The vast majority of end-users does not need to modify the core \
framework. These users need to provide two files only. One in which \
the brain volume to simulate is described and one in which the \
growth-rules are expressed.

Configuration file
------------------

The configuration file describes the brain volume to be simulated. \
Below an example:

.. literalinclude:: ../../examples/demo_attraction/demo_attraction.cfg
    :linenos:
    :language: none

Each configuration file contains at least four main sections:

:code:`[system]`
~~~~~~~~~~~~~~~~

This section contains entries directly related to the framework, rather \
than the volume and the neuronal structures to simulate. The following \
entries are included

- seed=21051982
- proxy_sub_port= 5599
- proxy_pub_port= 5560
- pull_port=55002
- time_out = 10000 *[currently not used]*
- no_cycles=30
- out_db=demo_attraction/demo_attraction.db
- synapse_distance = 5 *[optional]*
- syn_db = demo_attraction/syn.db *[optional]*

The :code:`seed` is used to initialize the system and for the randomized locations of \
the initial parts of the structures to generate. All :code:`_port` \
entries relate to the configuration of `ZeroMQ <http://zeromq.org/>`_ \
(also referred to as ZMQ). ZMQ is the messaging system used to implement \
the multi-agent system. The configured ports are TCP/IP ports used to \
communicate between the different components.

:code:`no_cycles` defines how many times each front has to be extended. \
:code:`out_db` specifies the location of the raw SQL output database. \
:code:`synapse_distance` is optional and sets the maximum distance \
between line segments (e.g., the frustum or cylinder between two \
successive fronts) at which a synapse could form. If set, these \
putative synapse locations will be recorded in a separate SQL \
database named with the value from :code:`syn_db`.

:code:`[substrate]`
~~~~~~~~~~~~~~~~~~~

This section describes the boundaries of the brain substrate.

.. note:: Currently, the brain volume is limited to a rectangular volume.

- dim_xyz = [100.0,100.0,100.0]

:code:`dim_xyz` determines the size of the rectangular volume, values \
represent [width,depth,height] (in NeuroMac, these correspond to x,y,z, \
which is different from "standard" physiological coordinates where y \
is used for the height or depth from the top surface, i.e., the pia \
in cortical slices). The left-bottom corner is always :math:`[0,0,0]`.

:code:`[sub_volumes]`
~~~~~~~~~~~~~~~~~~~~~~

Statements in this block define how the total volume should be decomposed \
into smaller blocks, whcih are subsequently parallelized by NeuroMaC.

.. note:: Currently, the volume decomposition is limited to rectangular \
   slicing of the volume.

- xa=1
- ya=1
- za=2

:code:`xa`, :code:`ya` and :code:`za` set the number of "slices" along \
the appropriate axis. The total number of subvolumes is hence \
:math:`SV = xa \times ya \times za`.


:code:`[cell_type_x]`
~~~~~~~~~~~~~~~~~~~~~~

This block is used to configure the neurites to be grown inside the \
simulated volume.

There are two distinct ways of generating many neurites simultaneously. \
The first way is illustrated in the above example and uses multiple \
:code:`cell_type_x` blocks. :code:`x` represents the name and can be \
any name (that would make a valid Python variable name, hence \
alphanumeric values and underscores). For each cell type the following \
variables need to be set.

- no_seeds=1
- algorithm = TestF_Left
- location = [[20,50,20],[20,50,20]]  
- soma_radius = 10

:code:`no_seeds` sets the number of instances of one cell type need \
to be created (here only 1). The :code:`algorithm` variable defines \
the growth-rules used by the fronts. :code:`location` is used to specify \
the initial position of the structure. The structure of the value is: \
[[x_min,y_min,z_min], [x_max,y_max,z_max]], which create a rectangular \
shape;  NeuroMaC uniformly samples a position from this rectangle. In \
case of only one seed, the location can be defined as any point in space \
(by setting x_min=xmax, y_min=y_max and z_min=z_max) 

.. warning:: The algorithm name must be in the :code:`$PYTHONPATH` and \
   must have the name :code:`<name>.py`. That is, if in the configuration \
   file the entry :code:`algorithm=my_rules` is listed, a Python file \
   named :code:`my_rules.py` must exist and must be in the path.

A second way to generate multiple structures is by setting the seed \
to any value > 1. In this case, the same growth-rules apply for all \
structures.

.. note:: Instantiating multiple structures with the same algorithm \
   does not mean they will be identical as the growth-rules usually \
   also include a random component.


Front specification
--------------------

The second part required for running a simulation using NeuroMaC is \
the specification of the growth-rules. Growth-rules are expressed \
in plain Python code.

The fixed part of the growth-rule is the definition so that NeuroMaC \
knows which function to execute. As such Python growth-rule *must* \
contain the following: ::

   def extend_front(front,seed,constellation) :
       # Do things, this front either branches, terminates or \
       # elongates. In these cases either two, none or one new front \
       # has to be returned

       # In case of elongation
       return [new_front]

A front is a :py:class:`front.Front` data structure. In NeuroMaC its \
role is double: both a physical entity in space with a location and \
radius but as well a phenomenological implementation of a growth-cone \
that contains the growth-rules.

Because Python is a full programming language there are no real \
limitations on how to implement the growth-rules. A few \
 :ref:`examples` are provided. It is strongly advised to start by \
adapting an example rather than to build a set of growth-rules from \
scratch.

Helper functions
~~~~~~~~~~~~~~~~

A few helper functions are packed with NeuroMaC to ease the implementation \
of growth-rules :ref:`apis`

Front implementation
~~~~~~~~~~~~~~~~~~~~
