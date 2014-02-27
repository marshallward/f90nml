======
f90nml
======

A Fortran 90 namelist parser


About f90nml
============

The f90nml_ module takes a Fortran 90 namelist file and parses it into a Python
``dict`` of namelist groups, each containing a ``dict`` of its variables.
Fortran data types are converted to equivalent Python types.


Usage
=====

To read a Fortran namelist file as a ``dict``, use the ``parse()`` method:

.. code:: python

   nml_dict = f90nml.parse(nml_filename)

To save a Python ``dict`` as a Fortran namelist file, use the ``save()``
method:

.. code:: python

   f90nml.save(my_nml, output_filename)

This method will abort if the output file already exists.


Notes
=====

The ``parse`` method produces an ``NmlDict``, which behaves as a ``dict`` with
case-insensitive keys, due to the case insensitivity of Fortran.


Licensing
=========

f90nml_ is distributed under the `Apache 2.0 License`_.


Contact
=======
Marshall Ward <python@marshallward.org>


.. _f90nml:
    https://github.com/marshallward/f90nml
.. _Apache 2.0 License:
    http://www.apache.org/licenses/LICENSE-2.0.txt
