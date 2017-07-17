"""Command line interface to f90nml.

:copyright: Copyright 2017 Marshall Ward, see AUTHORS for details.
:license: Apache License, Version 2.0, see LICENSE for details
"""

import argparse
import sys

import f90nml

def parse():
    parser = argparse.ArgumentParser()

    parser.add_argument('--version', action='version',
                        version='f90nml {}'.format(f90nml.__version__))

    if len(sys.argv) == 1:
        parser.print_help()
    else:
        args = parser.parse_args()
        print(args)
