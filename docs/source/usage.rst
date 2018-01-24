Usage
=====

The basic API is available for working with conventional namelist files and
performing simple operations, such as reading or modifying values.

Users who require more control over parsing and namelist output formatting
should create objects which can be controlled using the properties described
below.


Basic API
---------

.. autofunction:: f90nml.read

.. autofunction:: f90nml.write

.. autofunction:: f90nml.patch

Classes
-------

.. autoclass:: f90nml.parser.Parser
   :members:

.. autoclass:: f90nml.namelist.Namelist(default_start_index=None, [items])
   :members:
