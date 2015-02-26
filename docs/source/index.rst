===================================================================
``f90nml`` -- A Fortran namelist parser, generator, and manipulator
===================================================================

``f90nml`` is a Python module that provides a simple interface for the reading,
writing, and the general manipulation of Fortran namelist files.


Basic Usage
===========

Namelists are read through the ``f90nml`` parser and converted into an
``NmlDict`` object, which behaves like a standard Python ``dict``.  Values are
converted from Fortran data types to equivalent primitive Python types.

See the example below:




Basic Usage
-----------

.. autofunction:: f90nml.read

.. autofunction:: f90nml.write

.. autofunction:: f90nml.patch


