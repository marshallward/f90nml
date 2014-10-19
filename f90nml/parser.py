"""f90nml.parser
   =============

   Fortran namelist parser and tokenizer to convert contents into a hierarchy
   of dicts containing intrinsic Python data types.

   :copyright: Copyright 2014 Marshall Ward, see AUTHORS for details.
   :license: Apache License, Version 2.0, see LICENSE for details.
"""
import itertools
import shlex
from string import whitespace

from f90nml.fpy import pyfloat, pycomplex, pybool, pystr
from f90nml.namelist import NmlDict

class Parser(object):
    """shlex-based Fortran namelist parser."""

    def __init__(self, verbose=False, patch=None):

        # Token management
        self.tokens = None
        self.token = None
        self.prior_token = None

        # Debugging
        self.verbose = verbose

        # Patching
        self.patch = patch
        self.pfile = None


    def read(self, nml_fname):
        """Parse a Fortran 90 namelist file and store the contents.

        >>> from f90nml.parser import Parser
        >>> parser = Parser()
        >>> data_nml = parser.read('data.nml')"""

        nml_file = open(nml_fname, 'r')

        if self.patch:
            self.pfile = open(nml_fname + '~', 'w')

        f90lex = shlex.shlex(nml_file)
        f90lex.whitespace = ''
        f90lex.wordchars += '.-+'       # Include floating point tokens
        if self.patch:
            f90lex.commenters = ''
        else:
            f90lex.commenters = '!'

        self.tokens = iter(f90lex)

        nmls = NmlDict()

        for token in self.tokens:
            self.token = token

            try:
                # Check for classic group terminator
                if self.token == 'end':
                    self.update_tokens()

                # Ignore tokens outside of namelist groups
                while not self.token in tuple('&$'):
                    self.update_tokens()

                # Create the next namelist
                self.update_tokens()
                g_name = self.token

            except StopIteration:
                break

            g_vars = NmlDict()

            v_name = None

            # Populate the namelist group
            while g_name:

                if not self.token in ('=', '%', '('):
                    self.update_tokens()

                    # Skip commas separating objects
                    if self.token == ',':
                        self.update_tokens()

                # Diagnostic testing
                if self.verbose:
                    print('  tokens: {0} {1}'.format(repr(self.prior_token),
                                                     repr(self.token)))

                # Set the next active variable
                if self.token in ('=', '(', '%'):

                    nml_patch = self.patch.get(g_name, {})
                    v_name, v_values = self.parse_variable(patch=nml_patch)

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
                if self.token in ('/', '&', '$'):

                    # Append the grouplist to the namelist
                    if g_name in nmls:
                        g_update = nmls[g_name]

                        # Update to list of groups
                        if not type(g_update) is list:
                            g_update = [g_update]

                        g_update.append(g_vars)

                    else:
                        g_update = g_vars

                    nmls[g_name] = g_update

                    if self.verbose:
                        print('{0} saved with {1}'.format(g_name, g_vars))

                    # Reset state
                    g_name, g_vars = None, None

        nml_file.close()
        return nmls


    def parse_variable(self, patch=None):
        """Parse a variable and return its name and values."""

        v_name = self.prior_token
        v_values = []

        if self.token == '(':

            v_indices = self.parse_index()

            # TODO: Multidimensional support
            i_s = 1 if not v_indices[0][0] else v_indices[0][0]
            i_e = v_indices[0][1]
            i_r = 1 if not v_indices[0][2] else v_indices[0][2]

            if i_e:
                v_idx = iter(range(i_s, i_e, i_r))
            else:
                v_idx = (i_s + i_r * k for k in itertools.count())
        else:
            v_idx = None

        if self.token == '%':

            # Resolve the derived type

            self.update_tokens()
            self.update_tokens()
            v_att, v_att_vals = self.parse_variable()

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

            assert self.token == '='
            n_vals = None
            prior_ws_sep = ws_sep = False
            self.update_tokens()

            if v_name in patch:
                # TODO: Convert to fortran repr
                v_values = repr(patch.get(v_name))
                self.pfile.write(v_values)

                self.update_tokens(write_token=False)

            else:
                # Add variables until next variable trigger
                while (not self.token in ('=', '(', '%')
                       or (self.prior_token, self.token) == ('=', '(')):

                    # Check for repeated values
                    if self.token == '*':
                        n_vals = self.parse_value()
                        assert type(n_vals) is int
                        self.update_tokens()
                    elif not n_vals:
                        n_vals = 1

                    # First check for implicit null values
                    if self.prior_token in ('=', '%', ','):
                        if (self.token in (',', '/', '&', '$')
                                and not (self.prior_token == ','
                                         and self.token in ('/', '&', '$'))):
                            append_value(v_values, None, v_idx, n_vals)

                    elif self.prior_token == '*':

                        if not self.token in ('/', '&', '$'):
                            self.update_tokens()

                        if (self.token == '=' or (self.token in ('/', '&', '$')
                                                  and self.prior_token == '*')):
                            next_value = None
                        else:
                            next_value = self.parse_value()

                        append_value(v_values, next_value, v_idx, n_vals)

                    else:
                        next_value = self.parse_value()

                        # Check for escaped strings
                        if (v_values and (type(v_values[-1]) is str)
                                and type(next_value) is str and not prior_ws_sep):
                            v_values[-1] = self.prior_token[0].join([v_values[-1],
                                                                     next_value])
                        else:
                            append_value(v_values, next_value, v_idx, n_vals)



                    # Exit for end of nml group (/, &, $) or null broadcast (=)
                    if self.token in ('/', '&', '$', '='):
                        break
                    else:
                        prior_ws_sep = ws_sep
                        ws_sep = self.update_tokens()

        return v_name, v_values


    def parse_index(self):
        """Parse Fortran vector indices into a tuple of Python indices."""

        v_name = self.prior_token
        v_indices = []
        i_start = i_end = i_stride = None

        # Start index
        self.update_tokens()
        try:
            i_start = int(self.token)
            self.update_tokens()
        except ValueError:
            if self.token in (',', ')'):
                raise ValueError('{0} index cannot be empty.'.format(v_name))
            elif not self.token == ':':
                raise

        # End index
        if self.token == ':':
            self.update_tokens()
            try:
                i_end = 1 + int(self.token)
                self.update_tokens()
            except ValueError:
                if self.token == ':':
                    raise ValueError('{0} end index cannot be implicit '
                                     'when using stride.'.format(v_name))
                elif not self.token in (',', ')'):
                    raise
        elif self.token in (',', ')'):
            # Replace index with single-index range
            if i_start:
                i_end = 1 + i_start

        # Stride index
        if self.token == ':':
            self.update_tokens()
            try:
                i_stride = int(self.token)
            except ValueError:
                if self.token == ')':
                    raise ValueError('{0} stride index cannot be '
                                     'implicit.'.format(v_name))
                else:
                    raise

            if i_stride == 0:
                raise ValueError('{0} stride index cannot be zero.'
                                 ''.format(v_name))

            self.update_tokens()

        if not self.token in (',', ')'):
            raise ValueError('{0} index did not terminate '
                             'correctly.'.format(v_name))

        idx_triplet = (i_start, i_end, i_stride)
        v_indices.append((idx_triplet))
        self.update_tokens()

        return v_indices


    def parse_value(self):
        """Convert string repr of Fortran type to equivalent Python type."""
        v_str = self.prior_token

        # Construct the complex string
        if v_str == '(':
            v_re = self.token

            self.update_tokens()
            assert self.token == ','

            self.update_tokens()
            v_im = self.token

            self.update_tokens()
            assert self.token == ')'

            self.update_tokens()
            v_str = '({0}, {1})'.format(v_re, v_im)

        recast_funcs = [int, pyfloat, pycomplex, pybool, pystr]

        for f90type in recast_funcs:
            try:
                value = f90type(v_str)
                return value
            except ValueError:
                continue

        # If all tests fail, then raise ValueError
        # NOTE: I don't think this can happen anymore; string is now default
        raise ValueError('Could not convert {0} to a Python data type.'
                         ''.format(v_str))


    def update_tokens(self, write_token=True):
        """Update tokens to the next available values."""

        ws_sep = False
        next_token = next(self.tokens)

        # TODO: conditional
        if self.patch and write_token:
            self.pfile.write(self.token)

        while next_token in tuple(whitespace + '!'):

            if self.patch:
                if next_token == '!':
                    while not next_token == '\n':
                        self.pfile.write(next_token)
                        next_token = next(self.tokens)
                self.pfile.write(next_token)

            ws_sep = True
            next_token = next(self.tokens)

        self.token, self.prior_token = next_token, self.token

        return ws_sep


# Support functions

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


def merge_values(src, new):
    """Update a value list with a list of new or updated values."""

    l_min, l_max = (src, new) if len(src) < len(new) else (new, src)

    l_min.extend(None for i in range(len(l_min), len(l_max)))

    for i, val in enumerate(new):
        new[i] = val if val else src[i]

    return new
