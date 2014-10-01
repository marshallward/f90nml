"""f90nml
   ======

   A Fortran 90 namelist parser and generator.

   :copyright: Copyright 2014 Marshall Ward, see AUTHORS for details.
   :license: Apache License, Version 2.0, see LICENSE for details.
"""
__version__ = '0.8-dev'

from f90nml.parser import Parser

# Legacy API functions

def read(nml_fname, verbose=False):
    """Parse a Fortran 90 namelist file (data.nml) and store its contents.

    >>> nml = f90nml.read('data.nml')"""
    return Parser(verbose).read(nml_fname)

def write(nml, nml_fname, force=False):
    """Output namelist (nml) to a Fortran 90 namelist file (data.nml).

    >>> f90nml.write(nml, 'data.nml')"""
    nml.write(nml_fname, force)
