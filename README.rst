======
f90nml
======

A Python module for parsing Fortran namelist files

.. image:: https://travis-ci.org/marshallward/f90nml.svg?branch=master
    :target: https://travis-ci.org/marshallward/f90nml

.. image:: https://coveralls.io/repos/marshallward/f90nml/badge.png?branch=master
   :target: https://coveralls.io/r/marshallward/f90nml?branch=master

Documentation: http://f90nml.readthedocs.org/en/latest/


About f90nml
============

``f90nml`` is a Python module that provides a simple interface for the reading,
writing, and the general manipulation of Fortran namelist files.

A namelist file is parsed and converted into an ``Namelist`` object, which
behaves like a standard Python ``dict``.  Values are converted from Fortran
data types to equivalent primitive Python types.


Quick usage guide
=================

To read a namelist file ``sample.nml`` which contains the following namelists:

.. code:: fortran

   &config_nml
      input = 'wind.nc'
      steps = 864
      layout = 8, 16
      visc = 1e-4
      use_biharmonic = .false.
   /

we would use the following script:

.. code:: python

   import f90nml
   nml = f90nml.read('sample.nml')

which would would point ``nml`` to the following ``dict``:

.. code:: python

   nml = {'config_nml':
            {'input': 'wind.nc',
             'steps': 864,
             'layout': [8, 16],
             'visc': 0.0001,
             'use_biharmonic': False
            }
         }

File objects can also be used as inputs:

.. code:: python

   with open('sample.nml') as nml_file:
       nml = f90nml.read(nml_file)

To modify one of the values, say ``steps``, and save the output, just
manipulate the ``nml`` contents and write to disk using the ``write`` function:

.. code:: python

   nml['config_nml']['steps'] = 432
   nml.write('new_sample.nml')

Namelists can also be saved to file objects:

.. code:: python

   with open('target.nml') as nml_file:
      nml.write(nml_file)

To modify a namelist but preserve its comments and formatting, create a
namelist patch and apply it to a target file using the ``patch`` function:

.. code:: python

   patch_nml = {'config_nml': {'visc': 1e-6}}
   f90nml.patch('sample.nml', patch_nml, 'new_sample.nml')


Installation
============

``f90nml`` is available on PyPI and can be installed via pip::

   $ pip install f90nml

It is also available on Arch Linux via the AUR::

   $ git clone https://aur.archlinux.org/python-f90nml.git
   $ cd python-f90nml
   $ makepkg -sri

``f90nml`` is not yet available on other Linux distributions.

The latest version of ``f90nml`` can be installed from source::

   $ git clone https://github.com/marshallward/f90nml.git
   $ cd f90nml
   $ python setup.py install

Users without install privileges can append the ``--user`` flag to
``setup.py``::

   $ python setup.py install --user
