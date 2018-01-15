Notes
=====

Data types
----------

Fortran namelists do not contain any information about data type, which is
determined by the target variables of the Fortran executable.  ``f90nml``
infers the data type based on the value, but not all cases can be explicitly
resolved.

``f90nml`` tests values as one of each data type in the order listed below:

* Integer

* Floating point

* Complex floating point

* Logical (boolean)

* String

Strings act as a fallback type.  If a value cannot be matched to any other
value, then it is interpreted as a string.

In order to get the best results from ``f90nml``, it is best to follow these
guidelines:

* All strings should be enclosed by string delimiters (``'``, ``"``).

* Floating point values should use decimals (``.``) or `E notation`_.

* Array indices should be explicit

* Array values should be separated by commas (``,``)

.. _E notation: https://en.wikipedia.org/wiki/Scientific_notation#E_notation


Derived Types
-------------

User-defined types are saved as a nested hierarchy of ``dict``\ s.  For
example, the following namelist

.. code:: fortran

   &dtype_nml
      a%b%c = 1
   /

would be saved as the following ``Namelist``:

.. code:: python

   nml = {
      'dtype_nml': {
         'a': {
            'b': {
               'c': 1
            }
         }
      }
   }


Indexing
--------

The indexing of a vector is defined in the Fortran source file, and a namelist
can produce unexpected results if the starting index is implicit or
unspecified.  For example, the namelist below

.. code:: fortran

   &idx_nml
      v(1:2) = 5, 5
   /

will assign values to different indices of ``v`` depending on its starting
index, as in the examples below.

.. code:: fortran

   integer, dimension :: v(1:4)  ! Read as v = (5, 5, -, -)
   integer, dimension :: v(0:3)  ! Read as v = (-, 5, 5, -)

Without explicit knowledge of the starting index, it is not possible to
unambiguously represent the vector in Python.

In most cases, ``f90nml`` will internally assume a 1-based indexing, and will
only output the values explicitly listed in the namelist file.  If no index is
provided, then ``f90nml`` will not add indices to the record.

However, ``f90nml`` can still provide some level of control over the starting
index of a vector.  The starting index can be explicitly set using various
properties defined in the ``Parser`` and ``Namelist`` objects.  For more
information, see the class API.
