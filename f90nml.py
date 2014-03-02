"""f90nml.py
Parse fortran namelist files into dicts of standard Python data types.
Contact: Marshall Ward <python@marshallward.org>
---
Distributed as part of f90nml, Copyright 2014 Marshall Ward
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
"""
import os
import re
import shlex

__version__ = '0.1'

idx_end = (',', ')')

#---
def read(nml_fname):

    f = open(nml_fname, 'r')

    f90 = shlex.shlex(f)
    f90.commenters = '!'
    f90.escapedquotes = '\'"'
    f90.wordchars += '.-'   # Include decimal and negation characters
    tokens = iter(f90)

    # Store groups in case-insensitive dictionary
    nmls = NmlDict()

    for t in tokens:

        # Ignore tokens outside of namelist groups
        while t != '&':
            # TODO: '?' and '?=' support
            t = next(tokens)

        # NOTE: Current token is now '&'

        g_name = next(tokens)
        g_vars = NmlDict()

        v_name = None
        v_vals = []

        t = next(tokens)
        # NOTE: Current token is either a variable name or finalizer (/)
        while t != '/':

            prior_t = t
            t = next(tokens)

            # Determine index of vector variable
            if t == '(':

                v_name = prior_t
                v_indices = []
                i_start = i_end = i_stride = None

                # Start index
                t = next(tokens)
                try:
                    i_start = int(t)
                except ValueError:
                    if t in idx_end:
                        raise ValueError('{} index cannot be empty.'
                                         ''.format(v_name))
                    elif t == ':':
                        pass
                    else:
                        raise

                t = next(tokens)

                # End index
                if t == ':':
                    t = next(tokens)
                    try:
                        i_end = int(t)
                    except ValueError:
                        if t == ':':
                            raise ValueError('{} end index cannot be implicit '
                                             'when using stride.'
                                             ''.format(v_name))
                        elif t in idx_end:
                            pass
                        else:
                            raise
                    t = next(tokens)

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

                #XXX: debug
                print v_name, v_indices

            #TODO: =========
            #TODO: Start refactoring from here
            #TODO: =========

            # Set up new variable
            #if t == '=':
            #    if not v_name:
            #        v_name = prior_t

            #====
            # OLD CODE
            #====

            # If it's a variable name
            if v_name and not t == '=':

                # Test if varname contains a vector index
                match = re.search(r'\(\d+\)$', v_name)
                if match:
                    v_index = int(v_name[match.start()+1:-1])
                    v_name = v_name[:match.start()]
                else:
                    v_index = None

                # Parse the variable string
                if (prior_t, t) == (',', ','):
                    f90val = None
                elif prior_t != ',':
                    f90val = from_f90str(prior_t)
                else:
                    # Skip ahead to next token, do not append lone commas
                    continue

                if v_index and v_name in g_vars:
                    v_vals = g_vars[v_name]
                    if type(v_vals) != list:
                        v_vals = [v_vals]
                    try:
                        # NOTE: Fortran indexing starts at 1
                        v_vals[v_index-1] = f90val
                    except IndexError:
                        # Expand the list to accomodate out-of-range indices
                        size = len(v_vals)
                        v_vals.extend(None for i in range(size, v_index))
                        v_vals[v_index-1] = f90val
                else:
                    v_vals.append(f90val)

            # Finalize the current variable
            if v_name and (t == '=' or t == '/'):

                if len(v_vals) == 1:
                    v_vals = v_vals[0]
                g_vars[v_name] = v_vals

                # Deactivate the current variable
                v_name = None
                v_vals = []

            # Activate the next variable
            if t == '=':
                v_name = prior_t
                t = next(tokens)

        # Append the grouplist to the namelist (including empty groups)
        nmls[g_name] = g_vars

    f.close()

    return nmls


#---
def write(nml, nml_fname):

    if os.path.isfile(nml_fname):
        raise IOError('File {} already exists.'.format(nml_fname))

    f = open(nml_fname, 'w')

    for grp in sorted(nml.keys()):
        f.write('&{}\n'.format(grp))

        grp_vars = nml[grp]
        for v_name in sorted(grp_vars.keys()):

            v_val = grp_vars[v_name]

            if type(v_val) == list:
                v_str = ', '.join([to_f90str(v) for v in v_val])
            else:
                v_str = to_f90str(v_val)

            f.write('    {} = {}\n'.format(v_name, v_str))

        f.write('/\n')

    f.close()


#---
def to_f90str(v):
    """Convert primitive Python types to equivalent Fortran strings"""

    # TODO: Hash this somehow
    if type(v) is int:
        return str(v)
    elif type(v) is float:
        # TODO: Floating point precision?
        return str(v)
    elif type(v) is bool:
        return '.{}.'.format(str(v).lower())
    elif type(v) is complex:
        return '({}, {})'.format(v.real, v.imag)
    elif type(v) is str:
        return '\'{}\''.format(v)
    elif v is None:
        return ''
    else:
        raise ValueError('Type {} of {} cannot be converted to a Fortran type.'
                         ''.format(type(v), v))


#---
def from_f90str(s):
    """Convert string repr of Fortran type to equivalent Python type."""
    assert type(s) is str

    recast_funcs = [int, float, f90complex, f90bool, f90str]

    for f90type in recast_funcs:
        try:
            v = f90type(s)
            return v
        except ValueError:
            continue

    # If all test failed, then raise ValueError
    raise ValueError('Could not convert {} to a Python data type.'.format(s))


#---
def f90complex(s):
    assert type(s) == str

    if s[0] == '(' and s[-1] == ')' and len(s,split(',') == 2):
        s_re, s_im = s[1:-1].split(',', 1)

        # NOTE: Failed float(str) will raise ValueError
        return complex(float(s_re), float(s_im))
    else:
        raise ValueError('{} must be in complex number form (x, y)'.format(s))


#---
def f90bool(s):
    assert type(s) == str

    boolmap = {'t': True, 'f': False}

    match = re.match('\.?[tfTF]', s)
    if match:
        return boolmap[match.group()[-1].lower()]
    else:
        raise ValueError('{} is not a valid logical constant.'.format(s))


#---
def f90str(s):
    assert type(s) == str

    f90quotes = ["'", '"']

    if s[0] in f90quotes and s[-1] in f90quotes:
        return s[1:-1]

    raise ValueError


#---
class NmlDict(dict):
    def __setitem__(self, key, value):
        super(NmlDict, self).__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super(NmlDict, self).__getitem__(key.lower())
