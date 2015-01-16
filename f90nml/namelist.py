"""f90nml.namelist
   ===============

   Tools for creating Fortran namelist files from Python ``dict``s.

   :copyright: Copyright 2014 Marshall Ward, see AUTHORS for details.
   :license: Apache License, Version 2.0, see LICENSE for details.
"""
from __future__ import print_function

import os
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from f90nml import fpy


def write_nmlgrp(grp_name, grp_vars, nml_file):
    """Write namelist group to target file"""

    nml_file.write('&{0}\n'.format(grp_name))

    for v_name, v_val in grp_vars.items():

        for v_str in var_strings(v_name, v_val):

            nml_file.write('    {0}\n'.format(v_str))

    nml_file.write('/\n')


def var_strings(v_name, v_values, offset=0):
    """Convert namelist variable to list of fixed-width strings"""

    var_strs = []

    # Parse derived type contents
    if isinstance(v_values, dict):
        for f_name, f_vals in v_values.items():
            v_title = '%'.join([v_name, f_name])
            v_offset = offset + len(v_title)

            v_strs = var_strings(v_title, f_vals, v_offset)
            var_strs.extend(v_strs)

    # Parse an array of derived types
    elif isinstance(v_values, list) and all(isinstance(v, dict)
                                            for v in v_values):
        for idx, val in enumerate(v_values, start=1):
            v_title = v_name + '({0})'.format(idx)
            v_offset = offset + len(v_title)
            v_strs = var_strings(v_title, val, v_offset)
            var_strs.extend(v_strs)

    else:
        if not type(v_values) is list:
            v_values = [v_values]

        # Split into 72-character lines
        val_strs = []

        val_line = ''
        for v_val in v_values:

            if len(val_line) < 72 - len(v_name) - offset:
                val_line += fpy.f90repr(v_val) + ', '

            if len(val_line) >= 72 - len(v_name) - offset:
                val_strs.append(val_line)
                val_line = ''

        # Append any remaining values
        if val_line:
            val_strs.append(val_line[:-2])

        # Complete the set of values
        var_strs.append('{0} = {1}'.format(v_name, val_strs[0]).strip())

        for v_str in val_strs[1:]:
            var_strs.append(' ' * (3 + offset + len(v_name)) + v_str)

    return var_strs


class NmlDict(OrderedDict):
    """Case-insensitive Python dict"""

    def __contains__(self, key):
        return super(NmlDict, self).__contains__(key.lower())

    def __delitem__(self, key):
        return super(NmlDict, self).__delitem__(key.lower())

    def __getitem__(self, key):
        return super(NmlDict, self).__getitem__(key.lower())

    def __setitem__(self, key, value):
        super(NmlDict, self).__setitem__(key.lower(), value)


    def write(self, nml_path, force=False):
        """Output dict to a Fortran 90 namelist file."""

        if not force and os.path.isfile(nml_path):
            raise IOError('File {0} already exists.'.format(nml_path))

        with open(nml_path, 'w') as nml_file:
            for grp_name, grp_vars in self.items():
                if type(grp_vars) is list:
                    for g_vars in grp_vars:
                        write_nmlgrp(grp_name, g_vars, nml_file)
                else:
                    write_nmlgrp(grp_name, grp_vars, nml_file)
