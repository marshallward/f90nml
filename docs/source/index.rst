===================================================================
``f90nml`` -- A Fortran namelist parser, generator, and manipulator
===================================================================

``f90nml`` is a Python module that provides a simple interface for the reading,
writing, and the general manipulation of Fortran namelist files.

A namelist file is parsed and converted into an ``NmlDict`` object, which
behaves like a standard Python ``dict``.  Values are converted from Fortran
data types to equivalent primitive Python types.


Basic Usage
===========

Consider a namelist file, ``sample.nml`` which contains the following
namelist:

.. code:: fortran

   &config_nml
      input = 'wind.nc'
      steps = 864
      layout = 8, 16
      visc = 1e-4
      use_biharmonic = .false.
   /

In order to read this namelist into python, we would use the following script:

.. code:: python

   import f90nml
   nml = f90nml.read('sample.nml')


which would would set ``nml`` to the following ``dict``:

.. code:: python

   nml = {'config_nml':
            {'input': 'wind.nc',
             'steps': 864,
             'layout': [8, 16],
             'visc': 0.0001
             'use_biharmonic': False
            }
         }

To modify one of the values, say ``steps``, and save the output, just manipulate the ``nml`` contents and write to disk using the ``write`` function:

.. code:: python

   nml['config_nml']['steps'] = 432
   nml.write('new_sample.nml')


Basic Usage
-----------

.. autofunction:: f90nml.read

.. autofunction:: f90nml.write

.. autofunction:: f90nml.patch


