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

As an example, the namelist shown below:

.. code:: fortran

   &types
      ! fill me in
   /

would be converted to the equivalent ``dict``:

.. code:: python

   {'first':
       {'a': 1,
        'b': 2,
       }
    'second':
       {'c': 3,
        'd': 4
       }
   }


Basic Usage
-----------

.. autofunction:: f90nml.read

.. autofunction:: f90nml.write

.. autofunction:: f90nml.patch


