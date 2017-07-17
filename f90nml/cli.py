"""Command line interface to f90nml.

:copyright: Copyright 2017 Marshall Ward, see AUTHORS for details.
:license: Apache License, Version 2.0, see LICENSE for details
"""

import argparse
import json
import os
import sys

import f90nml

def parse():
    parser = argparse.ArgumentParser()

    parser.add_argument('--version', action='version',
                        version='f90nml {}'.format(f90nml.__version__))

    parser.add_argument('input')
    parser.add_argument('output', nargs='?')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    args = parser.parse_args()

    input_fname = args.input
    output_fname = args.output

    # Input config

    if input_fname:
        input_root, input_ext = os.path.splitext(input_fname)
        if input_ext == '.json':
            with open(input_fname) as input_file:
                input_data = json.load(input_file)
        else:
            # Assume unrecognised extensions are namelists
            input_data = f90nml.read(input_fname)
    else:
        input_data = {}

    # Target output

    if output_fname:
        output_root, output_ext = os.path.splitext(output_fname)

        if output_ext == '.nml':
            f90nml.write(input_data, output_fname)
        else:
            # TODO
            pass
    else:
        f90nml.write(input_data, sys.stdout)
