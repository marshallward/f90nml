Usage
=====

Basic API
---------

.. autofunction:: f90nml.read

.. autofunction:: f90nml.write

.. autofunction:: f90nml.patch

Classes
-------

.. autoclass:: f90nml.parser.Parser
   :members: comment_tokens, default_start_index, global_start_index,
             row_major, sparse_arrays, strict_logical, read

.. autoclass:: f90nml.namelist.Namelist
   :members: colwidth, end_comma, false_repr, floatformat, indent,
             logical_repr, start_index, true_repr, uppercase, write, patch,
             todict
