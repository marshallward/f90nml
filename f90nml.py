"""f90nml.py
Parse fortran namelist files into dicts of standard Python data types.
Contact: Marshall Ward <python@marshallward.org>
---
Distributed as part of f90nml, Copyright 2014 Marshall Ward
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
"""

from collections import OrderedDict
import itertools
import os
import shlex

__version__ = '0.4'


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
                print('  tokens: {} {}'.format(prior_t, t))

            # Set the next active variable
            if t in ('=', '(', '%'):
                v_name, v_values, t, prior_t = parse_f90var(tokens,
                                                                   t, prior_t)

                if v_name in g_vars:
                    v_prior_values = g_vars[v_name]
                    if type(v_prior_values) != list:
                        v_prior_values = [v_prior_values]

                    v_values = merge_values(v_prior_values, v_values)

                if len(v_values) == 0:
                    v_values = None
                elif len(v_values) == 1:
                    v_values = v_values[0]

                g_vars[v_name] = v_values

                # Deselect variable
                v_name = None
                v_values = []

            # Finalise namelist group
            if t in ('/', '&'):
                # Test for classic namelist finaliser
                if t == '&':
                    t, prior_t = next(tokens), t
                    assert t.lower() == 'end'

                # Append the grouplist to the namelist (including empty groups)
                nmls[g_name] = g_vars
                g_name, g_vars = None, None

    nml_file.close()

    return nmls


#---
def write(nml, nml_fname, force=False):
    """Output dict to a Fortran 90 namelist file."""

    if not force and os.path.isfile(nml_fname):
        raise IOError('File {} already exists.'.format(nml_fname))

    nml_file = open(nml_fname, 'w')

    for grp in nml.keys():
        nml_file.write('&{}\n'.format(grp))

        grp_vars = nml[grp]
        for v_name in grp_vars.keys():

            v_val = grp_vars[v_name]

            if type(v_val) == list:
                v_str = ', '.join([to_f90str(v) for v in v_val])
            else:
                v_str = to_f90str(v_val)

            nml_file.write('    {} = {}\n'.format(v_name, v_str))

        nml_file.write('/\n')

    nml_file.close()


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
        v_att, v_att_vals, t, prior_t = parse_f90var(tokens,
                                                                t, prior_t)

        # TODO: resolve indices
        next_value = {v_att: v_att_vals}
        append_value(v_values, next_value, v_idx)

    else:
        # Construct the variable array
        assert t == '='
        t, prior_t = next(tokens), t

        # Add variables until next variable trigger (excepting complex tokens)
        while not t in ('=', '(', '%') or (prior_t, t) == ('=', '('):

            # First check for implicit null values
            if prior_t in ('=', '%', ','):
                if t in (',', '/', '&') and not (prior_t, t) == (',', '/'):
                    append_value(v_values, None, v_idx)
            else:
                next_value, t = parse_f90val(tokens, t, prior_t)
                append_value(v_values, next_value, v_idx)

            # Exit at end of namelist group; otherwise process next value
            if t in ('/', '&'):
                break
            else:
                t, prior_t = next(tokens), t

    return v_name, v_values, t, prior_t


#---
def append_value(v_values, next_value, v_idx=None):
    """Update a list of parsed values with a new value."""

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
        return '.{}.'.format(str(value).lower())
    elif type(value) is complex:
        return '({}, {})'.format(value.real, value.imag)
    elif type(value) is str:
        return '\'{}\''.format(value)
    elif value is None:
        return ''
    else:
        raise ValueError('Type {} of {} cannot be converted to a Fortran type.'
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

        s = '({}, {})'.format(s_re, s_im)

    recast_funcs = [int, f90float, f90complex, f90bool, f90str]

    for f90type in recast_funcs:
        try:
            value = f90type(s)
            return value, t
        except ValueError:
            continue

    # If all test failed, then raise ValueError
    raise ValueError('Could not convert {} to a Python data type.'.format(s))


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
        raise ValueError('{} must be in complex number form (x, y)'.format(s))


#---
def f90bool(s):
    """Convert string repr of Fortran logical to Python logical."""
    assert type(s) == str

    try:
        s_bool = s[1].lower() if s.startswith('.') else s[0].lower()
    except IndexError:
        raise ValueError('{} is not a valid logical constant.'.format(s))

    if s_bool == 't':
        return True
    elif s_bool == 'f':
        return False
    else:
        raise ValueError('{} is not a valid logical constant.'.format(s))


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
            raise ValueError('{} index cannot be empty.'
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
                raise ValueError('{} end index cannot be implicit '
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
                raise ValueError('{} stride index cannot be '
                                 'implicit.'.format(v_name))
            else:
                raise

        if i_stride == 0:
            raise ValueError('{} stride index cannot be zero.'
                             ''.format(v_name))

        t = next(tokens)

    if not t in idx_end:
        raise ValueError('{} index did not terminate '
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
