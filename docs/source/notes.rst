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

   nml = {'dtype_nml':
            {'a':
               {'b':
                  {'c': 1}
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

Without explcit knowledge of the starting index, it is not possible to
unambiguously represent the vector in Python.

In most cases, ``f90nml`` will internally assume a 1-based indexing, and will
only output the values explicitly listed in the namelist file.  If no index is
provided, then ``f90nml`` will not add indices to the record.

However, ``f90nml`` can still provide some level of control over the starting
index of a vector.  The starting index can be explicitly set using the
properties defined below.  For a sample ``Parser`` object (``parser``), the
following property is available:

``parser.default_start_index`` (default: 1)

   The default starting index for any new vectors.  This primarily affects
   vectors whose values are set both with and without explicit indices.

   For the namelist ``idx.nml`` shown below,

   .. code:: fortran

      &idx_nml
          v(3:5) = 3, 4, 5
          v = 1, 2
      /

   the indices of the second entry in ``v`` are ambiguous.  The result for
   different values of ``default_start_index`` are shown below.

   .. code:: python

      >>> from f90nml import Parser
      >>> parser = Parser()
      >>> parser.default_start_index = 1  # Default
      >>> nml = parser.read('idx.nml')
      >>> nml['idx_nml']['v']
      [1, 2, 3, 4, 5]

      >>> parser.default_start_index = 0
      >>> nml = parser.read('idx.nml')
      >>> nml['idx_nml']['v']
      [1, 2, None, 3, 4, 5]

``parser.global_start_index`` (default: ``None``)

   Global override for starting index.  When unset, vectors are assumed to
   start at the lowest specified index.  If no index appears in the namelist,
   then ``default_start_index`` is used.

   When ``global_start_index`` is set, then all vectors will be created using
   this starting index.

   For the namelist file ``idx.nml`` shown below,

   .. code:: fortran

      &idx_nml
         v(3:5) = 3, 4, 5
      /

   then the following Python code behaves as shown below.

   .. code:: python

      >>> from f90nml import Parser
      >>> parser = Parser()
      >>> nml = parser.read('idx.nml')
      >>> nml['idx_nml']['v']
      [3, 4, 5]

      >>> parser.global_start_index = 1
      >>> nml = parser.read('idx.nml')
      >>> nml['idx_nml']['v']
      [None, None, 3, 4, 5]

   Currently, this property expects a scalar, and applies this value to all
   dimensions.

The starting indices are tracked within the namelist.  For a ``Namelist``
instance (``nml``), the property is specified below.

``nml.start_index``
   A ``dict`` containing the starting index for each vector saved in the
   namelist.  For the namelist ``vec.nml`` shown below,

   .. code:: fortran

      &vec_nml
          a = 1, 2, 3
          b(0:2) = 0, 1, 2
          c(3:5) = 3, 4, 5
          d(:,:) = 1, 2, 3, 4
      /

   the ``start_index`` contents are

   .. code:: python

      >>> import f90nml
      >>> nml = f90nml.read('vec.nml')
      >>> nml['vec_nml'].start_index
      {'d': [None, None], 'b': [0], 'c': [3]}

   The starting index of ``a`` is absent from ``start_index``, since its values
   cannot be assigned to any index without referring to the corresponding
   Fortran source.


Output formatting
-----------------

The output format of ``f90nml.write`` can be altered by modifying the
properties of the ``Namelist`` object.  The properties for a sample namelist
``nml`` are shown below.

``nml.colwidth`` (Default: 72)
   Maximum number of characters per line of the namelist file.  Tokens longer
   than ``colwidth`` are allowed to extend past this limit.

``nml.indent`` (Default: 4)
   Whitespace indentation.  This can be set to an integer, denoting the number
   of spaces, or to an explicit whitespace character, such as a tab (``\t``).

``nml.end_comma`` (Default: ``False``)
   Append a comma (``,``) to the end of each namelist entry.

``nml.uppercase`` (Default: ``False``)
   Display namelist and variable names in uppercase.

``nml.floatformat`` (Default: ``None``)
   Specify the floating point output format, as expected by Python's ``format``
   function.

``nml.logical_repr`` (Default: ``.false., .true.``)
   String representation of logical values ``False`` and ``True``.  The
   properties ``true_repr`` and ``false_repr`` are also provided as interfaces
   to the ``logical_repr`` tuple.


Comment tokens
--------------

Some Fortran programs will introduce alternative comment tokens (e.g. ``#``)
for internal preprocessing.

If you need to support these tokens, create a ``Parser`` object and set the
comment token as follows:

.. code:: python

   parser = f90nml.Parser()
   parser.comment_tokens += '#'
   nml = Parser.read('sample.nml')

Be aware that this is non-standard Fortran and could mangle any strings using
the ``#`` characters.  Characters inside string delimiters should be protected.


