"""f90nml
   ======

   A Fortran 90 namelist parser and generator.

   :copyright: Copyright 2014 Marshall Ward, see AUTHORS for details.
   :license: Apache License, Version 2.0, see LICENSE for details.
"""
from f90nml import namelist

__version__ = '0.8-dev'

# Legacy read() wrapper
def read(nml_fname, verbose=False):
    """Parse a Fortran 90 namelist file and store the contents in a ``dict``.

    >>> data_nml = f90nml.read('data.nml')"""

    return namelist.read(nml_fname, verbose)

# Legacy write() wrapper
def write(nml, nml_fname, force=False):
    """Output dict to a Fortran 90 namelist file."""

    namelist.write(nml, nml_fname, force)
