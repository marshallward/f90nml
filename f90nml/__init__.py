"""f90nml
   ======

   A Fortran 90 namelist parser and generator.

   :copyright: Copyright 2014 Marshall Ward, see AUTHORS for details.
   :license: Apache License, Version 2.0, see LICENSE for details.
"""
from f90nml.parser import Parser
from f90nml.namelist import Namelist

__version__ = '0.17'


def read(nml_path, row_major=None, strict_logical=None):
    """Parse a Fortran 90 namelist file with file path ``nml_path``  return its
    contents as a ``Namelist``.

    >>> nml = f90nml.read('data.nml')

    This function is equivalent to the ``read`` function of the ``Parser``
    object.

    >>> parser = f90nml.Parser()
    >>> nml = parser.read('data.nml')

    Multidimensional array data contiguity is preserved by default, so that
    column-major Fortran data is represented as row-major Python list of
    lists.

    The ``row_major`` flag will reorder the data to preserve the index rules
    between Fortran to Python, but the data will be converted to row-major form
    (with respect to Fortran).

    The ``strict_logical`` flag will limit the parsing of non-delimited logical
    strings as logical values.  The default value is ``True``.

    When ``strict_logical`` is enabled, only ``.true.``, ``.t.``, ``true``, and
    ``t`` are interpreted as ``True``, and only ``.false.``, ``.f.``,
    ``false``, and ``.false.`` are interpreted as false.

    When ``strict_logical`` is disabled, any value starting with ``.t`` or
    ``t`` are interpreted as ``True``, while any string starting with ``.f`` or
    ``f`` is interpreted as ``False``."""

    parser = Parser()
    parser.row_major = row_major
    parser.strict_logical = strict_logical

    return parser.read(nml_path)


def write(nml, nml_path, force=False):
    """Output namelist ``nml`` to a Fortran 90 namelist file with file path
    ``nml_path``.

    >>> f90nml.write(nml, 'data.nml')

    This function is equivalent to the ``write`` function of the ``Namelist``
    object ``nml``.

    >>> nml.write('data.nml')

    By default, ``write`` will not overwrite an existing file.  To override
    this, use the ``force`` flag.

    >>> nml.write('data.nml', force=True)"""

    # Promote dicts to Namelists
    if not isinstance(nml, Namelist) and isinstance(nml, dict):
        nml_in = Namelist(nml)
    else:
        nml_in = nml

    nml_in.write(nml_path, force=force)


def patch(nml_path, nml_patch, out_path=None, row_major=None,
          strict_logical=None):
    """Create a new namelist based on an input namelist and reference dict.

    >>> f90nml.patch('data.nml', nml_patch, 'patched_data.nml')

    This function is equivalent to the ``read`` function of the ``Parser``
    object with the patch output arguments.

    >>> parser = f90nml.Parser()
    >>> nml = parser.read('data.nml', nml_path, 'patched_data.nml')

    A patched namelist file will retain any formatting or comments from the
    original namelist file.  Any modified values will be formatted based on the
    settings of the ``Namelist`` object."""

    parser = Parser()
    parser.row_major = row_major
    parser.strict_logical = strict_logical

    return parser.read(nml_path, nml_patch, out_path)
