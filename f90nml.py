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
        v_idx = None
        v_vals = []

        # Current token is either a variable name or finalizer (/, &)

        # Populate the namelist group
        while g_name:

            if not v_name:
                t, prior_t = next(tokens), t

                # Skip commas separating objects
                if t == ',':
                    t, prior_t = next(tokens), t

            # Diagnostic testing
            if verbose:
                print('  tokens: {} {}'.format(prior_t, t))

            while v_name:

                t, prior_t = next(tokens), t

                if verbose:
                    print('    vstate: {} {} {}'.format(v_name, v_idx, v_vals))
                    print('    tokens: {} {}'.format(prior_t, t))

                # Parse the prior token value
                # TODO: Add '%' to first tuple
                if (not t in ('(', '=') or prior_t == '=') \
                        and not (prior_t, t) == (',', '/'):
                    # Parse the variable string
                    if prior_t in ('=', ','):
                        if t in (',', '/', '&'):
                            next_value = None
                        else:
                            continue
                    else:
                        next_value, t = parse_f90val(tokens, t, prior_t)

                    if v_idx:

                        v_i = next(v_idx)

                        if v_name in g_vars:
                            v_vals = g_vars[v_name]
                            if type(v_vals) != list:
                                v_vals = [v_vals]

                        try:
                            # Default Fortran indexing starts at 1
                            v_vals[v_i - 1] = next_value
                        except IndexError:
                            # Expand list to accomodate out-of-range indices
                            size = len(v_vals)
                            v_vals.extend(None for i in range(size, v_i))
                            v_vals[v_i - 1] = next_value
                    else:
                        v_vals.append(next_value)

                # Save then deactivate the current variable
                # TODO: Add '%'
                if t in ('(', '=', '/', '&'):

                    if len(v_vals) == 0:
                        v_vals = None
                    elif len(v_vals) == 1:
                        v_vals = v_vals[0]

                    g_vars[v_name] = v_vals

                    v_name = None
                    v_vals = []

            # Set the next active variable
            # TODO: Add '%' to the list
            if t in ('=', '('):
                v_name = prior_t
                v_idx = None

                # Parse the indices of the current variable
                if t == '(':
                    v_name, v_indices, t = parse_f90idx(tokens, t, prior_t)

                    # TODO: Multidimensional support
                    # TODO: End index support (currently ignored)
                    i_s = 1 if not v_indices[0][0] else v_indices[0][0]
                    i_r = 1 if not v_indices[0][2] else v_indices[0][2]
                    v_idx = itertools.count(i_s, i_r)

                # Identify any derived type fields
                if t == '%':
                    # TODO: Recurse into a new parsing of variable name
                    pass

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
def parse_f90var(tokens, t, prior_t):
    """Not sure how this will work yet"""

    pass


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
            i_end = int(t)
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
            i_end = i_start

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

    return v_name, v_indices, t


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


#---
class F90DerivedType(object):
    """Fortran 90 derived type"""

    def __init__(self):
        f90attrs = {}
