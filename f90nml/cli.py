"""Command line interface to f90nml.

:copyright: Copyright 2017 Marshall Ward, see AUTHORS for details.
:license: Apache License, Version 2.0, see LICENSE for details
"""

import argparse
import io
import json
import os
import sys
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

import f90nml
try:
    import yaml
    has_yaml = True
except ImportError:
    has_yaml = False


def parse():
    parser = argparse.ArgumentParser()

    parser.add_argument('--version', action='version',
                        version='f90nml {0}'.format(f90nml.__version__))

    parser.add_argument('--group', '-g', action='store')
    parser.add_argument('--set', '-s', action='append')
    parser.add_argument('--patch', '-p', action='store_false')

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
        _, input_ext = os.path.splitext(input_fname)
        if input_ext == '.json':
            with open(input_fname) as input_file:
                input_data = json.load(input_file)

        elif has_yaml and input_ext == '.yaml':
            with open(input_fname) as input_file:
                input_data = yaml.safe_load(input_file)

        else:
            # Assume unrecognised extensions are namelists
            input_data = f90nml.read(input_fname)
    else:
        input_data = {}

    input_data = f90nml.Namelist(input_data)

    # Replace any values

    if args.set:
        if not args.group:
            # Use the first available group
            grp = list(input_data.keys())[0]
            print('f90nml: warning: Assuming variables are in group \'{0}\'.'
                  ''.format(grp))
        else:
            grp = args.group

        update_nml = '&{0} {1} /\n'.format(grp, ', '.join(args.set))
        with io.StringIO(update_nml) as update_io:
            update_data = f90nml.read(update_io)

        input_data[grp].update(update_data[grp])

    # Target output

    if output_fname:
        _, output_ext = os.path.splitext(output_fname)

        # TODO: Better control of output format
        if output_ext == '.json':
            input_data = input_data.todict(decomplex=True)
            with open(output_fname, 'w') as output_file:
                json.dump(input_data, output_file,
                          indent=4, separators=(',', ': '))
                output_file.write('\n')

        elif output_ext == '.yaml':
            if has_yaml:
                input_data = input_data.todict(decomplex=True)
                with open(output_fname, 'w') as output_file:
                    yaml.dump(input_data, output_file,
                              default_flow_style=False)
            else:
                print('f90nml: error: YAML module could not be found.')
                sys.exit(-1)

        else:
            # Default to namelist output
            f90nml.write(input_data, output_fname)
    else:
        # TODO: Combine with extension output
        f90nml.write(input_data, sys.stdout)
