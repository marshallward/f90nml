"""f90nml
   ======

   A Fortran 90 namelist parser and generator.

   :copyright: Copyright 2014 Marshall Ward, see AUTHORS for details.
   :license: Apache License, Version 2.0, see LICENSE for details.
"""

from collections import OrderedDict
import itertools
import os
import shlex
import textwrap

__version__ = '0.6.2'


#---
def read(nml_fname, verbose=False):
    """Parse a Fortran 90 namelist file and store the contents in a ``dict``.

    >>> data_nml = f90nml.read('data.nml')"""

    nml_file = open(nml_fname, 'r')

    f90lex = shlex.shlex(nml_file)
    f90lex.commenters = '!'
    f90lex.escapedquotes = '\'"'
    f90lex.wordchars += '.-+'      # Include floating point characters
    tokens = iter(f90lex)

    # Store groups in case-insensitive dictionary
    nmls = NmlDict()

    for t in tokens:

        # Check for classic group terminator
        if t == 'end':
            try:
                t, prior_t = next(tokens), t
            except StopIteration:
                break

        # Ignore tokens outside of namelist groups
        while t != '&':
            t, prior_t = next(tokens), t

        # Current token is now '&'

        # Create the next namelist
        g_name = next(tokens)
        g_vars = NmlDict()

        v_name = None

        # Current token is either a variable name or finalizer (/, &)

        # Populate the namelist group
        while g_name:

            if not t in ('=', '%', '('):
                t, prior_t = next(tokens), t

                # Skip commas separating objects
                if t == ',':
                    t, prior_t = next(tokens), t

            # Diagnostic testing
            if verbose:
                print('  tokens: {0} {1}'.format(prior_t, t))

            # Set the next active variable
            if t in ('=', '(', '%'):
                v_name, v_values, t, prior_t = parse_f90var(tokens, t, prior_t)

                if v_name in g_vars:
                    v_prior_values = g_vars[v_name]
                    if not type(v_prior_values) is list:
                        v_prior_values = [v_prior_values]

                    v_values = merge_values(v_prior_values, v_values)

                if len(v_values) == 0:
                    v_values = None
                elif len(v_values) == 1:
                    v_values = v_values[0]

                if v_name in g_vars and type(g_vars[v_name]) is NmlDict:
                    g_vars[v_name].update(v_values)
                else:
                    g_vars[v_name] = v_values

                # Deselect variable
                v_name = None
                v_values = []

            # Finalise namelist group
            if t in ('/', '&'):

                # Append the grouplist to the namelist (including empty groups)
                if g_name in nmls:
                    g_update = nmls[g_name]

                    # Update to list of groups
                    if not type(g_update) is list:
                        g_update = [g_update]

                    g_update.append(g_vars)

                else:
                    g_update = g_vars

                nmls[g_name] = g_update

                if verbose:
                    print('{0} saved with {1}'.format(g_name, g_vars))

                # Reset state
                g_name, g_vars = None, None

    nml_file.close()

    return nmls


#---
def write(nml, nml_fname, force=False):
    """Output dict to a Fortran 90 namelist file."""

    if not force and os.path.isfile(nml_fname):
        raise IOError('File {0} already exists.'.format(nml_fname))

    nml_file = open(nml_fname, 'w')

    for grp_name, grp_vars in nml.items():

        if type(grp_vars) is list:
            for g_vars in grp_vars:
                write_nmlgrp(grp_name, g_vars, nml_file)
        else:
            write_nmlgrp(grp_name, grp_vars, nml_file)

    nml_file.close()


#---
def write_nmlgrp(grp_name, grp_vars, nml_file):

    nml_file.write('&{0}\n'.format(grp_name))

    for v_name, v_val in grp_vars.items():

        for v_str in var_strings(v_name, v_val):

            nml_file.write('    {0}\n'.format(v_str))

    nml_file.write('/\n')


#---
def var_strings(v_name, v_values, offset=0):

    var_strs = []

    if type(v_values) in (dict, NmlDict):

        for f_name, f_vals in v_values.items():
            v_strs = var_strings(f_name, f_vals, offset + 1 + len(v_name))
            var_strs.append('%'.join([v_name, v_strs[0]]))
            var_strs.extend(v_strs[1:])
    else:
        if not type(v_values) is list:
            v_values = [v_values]

        # Split into 72-character lines
        val_strs = []

        val_line = ''
        for v_val in v_values:

            # TODO: Calculate offsets for varnames
            if len(val_line) < 72 - len(v_name) - offset:
                val_line += to_f90str(v_val) + ', '

            # TODO: Calculate offsets for varnames
            if len(val_line) >= 72 - len(v_name) - offset:
                val_strs.append(val_line)
                val_line = ''

        # Append any remaining values
        if val_line:
            val_strs.append(val_line[:-2])

        # Complete the set of values
        var_strs.append('{0} = {1}'.format(v_name, val_strs[0]))

        for v_str in val_strs[1:]:
            var_strs.append('{0}   {1}'
                            ''.format((offset + len(v_name)) * ' ', v_str))

    return var_strs


#---
def parse_f90var(tokens, t, prior_t):
    """Parse a variable and return its name and values."""

    v_name = prior_t
    v_values = []

    # Parse the indices of the current variable
    if t == '(':
        v_indices, t = parse_f90idx(tokens, t, prior_t)

        # TODO: Multidimensional support
        i_s = 1 if not v_indices[0][0] else v_indices[0][0]
        i_e = v_indices[0][1]
        i_r = 1 if not v_indices[0][2] else v_indices[0][2]

        if i_e:
            v_idx = iter(range(i_s, i_e, i_r))
        else:
            v_idx = itertools.count(i_s, i_r)
    else:
        v_idx = None

    if t == '%':
        # Resolve the derived type
        t, prior_t = next(tokens), t
        t, prior_t = next(tokens), t
        v_att, v_att_vals, t, prior_t = parse_f90var(tokens, t, prior_t)

        # TODO: resolve indices
        next_value = NmlDict()

        if len(v_att_vals) == 0:
            v_att_vals = None
        elif len(v_att_vals) == 1:
            v_att_vals = v_att_vals[0]

        next_value[v_att] = v_att_vals

        append_value(v_values, next_value, v_idx)

    else:
        # Construct the variable array

        assert t == '='
        n_vals = None
        t, prior_t = next(tokens), t

        # Add variables until next variable trigger (excepting complex tokens)
        while not t in ('=', '(', '%') or (prior_t, t) == ('=', '('):

            # Check for repeated values
            if t == '*':
                n_vals, t = parse_f90val(tokens, t, prior_t)
                assert type(n_vals) is int
                t, prior_t = next(tokens), t
            elif not n_vals:
                n_vals = 1

            # First check for implicit null values
            if prior_t in ('=', '%', ','):
                if t in (',', '/', '&') and not (
                        prior_t == ',' and t in ('/', '&')):
                    append_value(v_values, None, v_idx, n_vals)

            elif prior_t == '*':

                if not t in ('/', '&'):
                    t, prior_t = next(tokens), t

                if t == '=' or (t in ('/', '&') and prior_t == '*'):
                    next_value = None
                else:
                    next_value, t = parse_f90val(tokens, t, prior_t)

                append_value(v_values, next_value, v_idx, n_vals)

            else:
                next_value, t = parse_f90val(tokens, t, prior_t)
                append_value(v_values, next_value, v_idx, n_vals)

            # Exit for end of nml group (/, &) or end of null broadcast (=)
            if t in ('/', '&', '='):
                break
            else:
                t, prior_t = next(tokens), t

    return v_name, v_values, t, prior_t


#---
def append_value(v_values, next_value, v_idx=None, n_vals=1):
    """Update a list of parsed values with a new value."""

    for _ in range(n_vals):
        if v_idx:
            v_i = next(v_idx)

            try:
                # Default Fortran indexing starts at 1
                v_values[v_i - 1] = next_value
            except IndexError:
                # Expand list to accommodate out-of-range indices
                size = len(v_values)
                v_values.extend(None for i in range(size, v_i))
                v_values[v_i - 1] = next_value
        else:
            v_values.append(next_value)


#---
def to_f90str(value):
    """Convert primitive Python types to equivalent Fortran strings"""

    if type(value) is int:
        return str(value)
    elif type(value) is float:
        return str(value)
    elif type(value) is bool:
        return '.{0}.'.format(str(value).lower())
    elif type(value) is complex:
        return '({0}, {1})'.format(value.real, value.imag)
    elif type(value) is str:
        return '\'{0}\''.format(value)
    elif value is None:
        return ''
    else:
        raise ValueError('Type {0} of {1} cannot be converted to a Fortran type.'
                         ''.format(type(value), value))


#---
def parse_f90val(tokens, t, s):
    """Convert string repr of Fortran type to equivalent Python type."""
    assert type(s) is str

    # Construct the complex string
    if s == '(':
        s_re = t
        next(tokens)
        s_im = next(tokens)

        # Bypass the right parenthesis
        t = next(tokens)
        assert t == ')'

        t = next(tokens)

        s = '({0}, {1})'.format(s_re, s_im)

    recast_funcs = [int, f90float, f90complex, f90bool, f90str]

    for f90type in recast_funcs:
        try:
            value = f90type(s)
            return value, t
        except ValueError:
            continue

    # If all test failed, then raise ValueError
    raise ValueError('Could not convert {0} to a Python data type.'.format(s))


#---
def f90float(s):
    """Convert string repr of Fortran floating point to Python double"""

    return float(s.lower().replace('d', 'e'))


#---
def f90complex(s):
    """Convert string repr of Fortran complex to Python complex."""
    assert type(s) == str

    if s[0] == '(' and s[-1] == ')' and len(s.split(',')) == 2:
        s_re, s_im = s[1:-1].split(',', 1)

        # NOTE: Failed float(str) will raise ValueError
        return complex(f90float(s_re), f90float(s_im))
    else:
        raise ValueError('{0} must be in complex number form (x, y)'.format(s))


#---
def f90bool(s):
    """Convert string repr of Fortran logical to Python logical."""
    assert type(s) == str

    try:
        s_bool = s[1].lower() if s.startswith('.') else s[0].lower()
    except IndexError:
        raise ValueError('{0} is not a valid logical constant.'.format(s))

    if s_bool == 't':
        return True
    elif s_bool == 'f':
        return False
    else:
        raise ValueError('{0} is not a valid logical constant.'.format(s))


#---
def f90str(s):
    """Convert string repr of Fortran string to Python string."""
    assert type(s) == str

    f90quotes = ["'", '"']

    if s[0] in f90quotes and s[-1] in f90quotes:
        return s[1:-1]

    raise ValueError


#---
def parse_f90idx(tokens, t, prior_t):
    """Parse Fortran vector indices into a tuple of Python indices."""

    idx_end = (',', ')')

    v_name = prior_t
    v_indices = []
    i_start = i_end = i_stride = None

    # Start index
    t = next(tokens)
    try:
        i_start = int(t)
        t = next(tokens)
    except ValueError:
        if t in idx_end:
            raise ValueError('{0} index cannot be empty.'
                             ''.format(v_name))
        elif not t == ':':
            raise

    # End index
    if t == ':':
        t = next(tokens)
        try:
            i_end = 1 + int(t)
            t = next(tokens)
        except ValueError:
            if t == ':':
                raise ValueError('{0} end index cannot be implicit '
                                 'when using stride.'
                                 ''.format(v_name))
            elif not t in idx_end:
                raise
    elif t in idx_end:
        # Replace index with single-index range
        if i_start:
            i_end = 1 + i_start

    # Stride index
    if t == ':':
        t = next(tokens)
        try:
            i_stride = int(t)
        except ValueError:
            if t == ')':
                raise ValueError('{0} stride index cannot be '
                                 'implicit.'.format(v_name))
            else:
                raise

        if i_stride == 0:
            raise ValueError('{0} stride index cannot be zero.'
                             ''.format(v_name))

        t = next(tokens)

    if not t in idx_end:
        raise ValueError('{0} index did not terminate '
                         'correctly.'.format(v_name))

    idx_triplet = (i_start, i_end, i_stride)
    v_indices.append((idx_triplet))
    t = next(tokens)

    return v_indices, t


#---
def merge_values(src, new):
    """Update a value list with a list of new or updated values."""

    l_min, l_max = (src, new) if len(src) < len(new) else (new, src)

    l_min.extend(None for i in range(len(l_min), len(l_max)))

    for i, val in enumerate(new):
        new[i] = val if val else src[i]

    return new


#---
class NmlDict(OrderedDict):
    """Case-insensitive Python dict"""
    def __setitem__(self, key, value):
        super(NmlDict, self).__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super(NmlDict, self).__getitem__(key.lower())


    def write(self, path, force=False):
        """Wrapper to the ``write`` method"""
        write(self, path, force)
