======
f90nml
======

A Fortran 90 namelist parser


About f90nml
============

This module takes a Fortran 90 namelist file and parses it into a dict of
namelist groups containing dicts of group variables. Fortran data types are
converted to equivalent Python types.


Usage
=====

In order to read a Fortran namelist file as a ``dict``, use the ``parse()``
method:

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

f90nml is licensed under the `Python Software Foundation License`.

..
