======
f90nml
======

A Python module for parsing Fortran namelist files

.. image:: https://travis-ci.org/marshallward/f90nml.svg?branch=master
    :target: https://travis-ci.org/marshallward/f90nml

.. image:: https://coveralls.io/repos/marshallward/f90nml/badge.png?branch=master
   :target: https://coveralls.io/r/marshallward/f90nml?branch=master


About f90nml
============

The f90nml_ module takes a Fortran 90 namelist file and parses it into a Python
``dict`` of namelist groups, each containing a ``dict`` of its variables.
Fortran data types are converted to equivalent Python types.


Usage
=====

To read a Fortran namelist file as a ``dict``, use the ``read()`` method:

.. code:: python

   nml = f90nml.read(nml_filename)

To save a ``dict`` as a Fortran namelist file, use the ``write()`` method:

.. code:: python

   nml.write(output_filename)

The ``write()`` method will abort if the output file already exists.

To patch an existing file against a ``dict``, use the ``patch()`` method:

.. code:: python

   nml.patch(input_filename, nml_patch, output_filename)

Namelist fields in ``input_filename`` will be checked against ``nml_patch`` and
updated with new values.  Fields in ``nml_patch`` which do not exist in
``input_filename`` will be appended to the namelist groups.  The function
returns the updated namelist ``dict`` and saves the patched namelist file to
``output_filename``.

The ``patch()`` method currently does not allow patching of vectors or user
types (``%``), but may be included in the future.


Additional Features
-------------------

Derived types
+++++++++++++

Additional ``NmlDict``\ s are created to traverse user-defined types. For
example, if you want to access ``z`` in the following namelist:

.. code:: fortran

   &dtype_nml
      x%y%z = 1
   /

then ``z`` can be accessed in the equivalent namelist ``nml`` by typing

.. code:: python

   z = nml['dtype_nml']['x']['y']['z']


Overwriting an existing file
++++++++++++++++++++++++++++

To overwrite an existing file when using the ``write`` method, use the
``force`` flag:

.. code:: python

   nml.write(nml_filename, force=True)


Notes
=====

The ``read`` method produces an ``NmlDict``, which behaves as a ``dict`` with
case-insensitive keys, due to the case insensitivity of Fortran. This
implementation is currently not a true case-insensitive ``dict``, and is only
intended to accommodate individual references and assignments.

In a Fortran executable, the data types of values in the namelist files are set
by the corresponding variables within the program, and cannot in general be
determined from the namelist file alone. Therefore, ``f90nml`` only makes an
approximate guess about its data type.

The following namelist features are currently not supported:

* Multidimensional vector assignment (``v(:,:) = 1, 2, 3, 4``)
* Upcast vector elements if components differ (``x(i) = 1, x(j) = 2.0``)
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
