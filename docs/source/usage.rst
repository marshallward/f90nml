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
   :members: comment_tokens, dense_arrays, row_major, strict_logical

.. autoclass:: f90nml.namelist.Namelist
   :members: colwidth, end_comma, false_repr, floatformat, indent,
             logical_repr, patch, todict, true_repr, uppercase

.. autoclass:: f90nml.findex.FIndex
   :members:
