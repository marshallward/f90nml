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

To read a Fortran namelist file as a ``dict``, use the ``read()`` method:

.. code:: python

   nml_dict = f90nml.read(nml_filename)

To output a Python ``dict`` as a Fortran namelist file, use the ``write()``
method:

.. code:: python

   f90nml.write(my_nml, output_filename)

This method will abort if the output file already exists.


Notes
=====

The ``read`` method produces an ``NmlDict``, which behaves as a ``dict`` with
case-insensitive keys, due to the case insensitivity of Fortran. This
implementation is currently not a true case-insensitive ``dict``, and is only
intended to accomodate individual references and assignments.

The following namelist features are currently not supported:

* Complex numbers
* Index range support (``v(i:j) = c``)
* Repeated indexing (``v = r*c, r*``)
* Upcast vector elements if components differ (``x(i) = int, x(j) = float``)
* Escape on repeated quotes (``'This doesn''t parse correctly'``)
* Type character resolver (``x%y = c``)
* stdin/stdout support (``?``, ``?=``)


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
