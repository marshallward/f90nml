"""f90nml.parser
   =============

   Fortran namelist parser and tokenizer to convert contents into a hierarchy
   of dicts containing intrinsic Python data types.

   :copyright: Copyright 2014 Marshall Ward, see AUTHORS for details.
   :license: Apache License, Version 2.0, see LICENSE for details.
"""
import copy
import itertools
import shlex
from string import whitespace

from f90nml.fpy import pyfloat, pycomplex, pybool, pystr
from f90nml.namelist import NmlDict


class Parser(object):
    """shlex-based Fortran namelist parser."""

    def __init__(self):

        # Token management
        self.tokens = None
        self.token = None
        self.prior_token = None

        # Patching
        self.pfile = None

    def read(self, nml_fname, nml_patch_in=None, patch_fname=None):
        """Parse a Fortran 90 namelist file and store the contents.

        >>> from f90nml.parser import Parser
        >>> parser = Parser()
        >>> data_nml = parser.read('data.nml')"""

        nml_file = open(nml_fname, 'r')

        if nml_patch_in:

            if not isinstance(nml_patch_in, dict):
                nml_file.close()
                raise ValueError('Input patch must be a dict or an NmlDict.')

            nml_patch = copy.deepcopy(NmlDict(nml_patch_in))

            if not patch_fname:
                patch_fname = nml_fname + '~'
            elif nml_fname == patch_fname:
                nml_file.close()
                raise ValueError('f90nml: error: Patch filepath cannot be the '
                                 'same as the original filepath.')
            self.pfile = open(patch_fname, 'w')
        else:
            nml_patch = NmlDict()

        f90lex = shlex.shlex(nml_file)
        f90lex.whitespace = ''
        f90lex.wordchars += '.-+'       # Include floating point tokens
        if nml_patch:
            f90lex.commenters = ''
        else:
            f90lex.commenters = '!'

        self.tokens = iter(f90lex)

        nmls = NmlDict()

        # TODO: Replace "while True" with an update_token() iterator
        self.update_tokens(write_token=False)
        while True:
            try:
                # Check for classic group terminator
                if self.token == 'end':
                    self.update_tokens()

                # Ignore tokens outside of namelist groups
                while self.token not in ('&', '$'):
                    self.update_tokens()

            except StopIteration:
                break

            # Create the next namelist
            self.update_tokens()
            g_name = self.token

            g_vars = NmlDict()
            v_name = None

            grp_patch = nml_patch.get(g_name, {})

            # Populate the namelist group
            while g_name:

                if self.token not in ('=', '%', '('):
                    self.update_tokens()

                # Set the next active variable
                if self.token in ('=', '(', '%'):

                    try:
                        v_name, v_values = self.parse_variable(
                            g_vars, patch_nml=grp_patch)
                    except ValueError:
                        nml_file.close()
                        if self.pfile:
                            self.pfile.close()
                        raise

                    if v_name in g_vars:
                        v_prior_values = g_vars[v_name]
                        v_values = merge_values(v_prior_values, v_values)

                    if v_name in g_vars and isinstance(g_vars[v_name], dict):
                        g_vars[v_name].update(v_values)
                    else:
                        g_vars[v_name] = v_values

                    # Deselect variable
                    v_name = None
                    v_values = []

                # Finalise namelist group
                if self.token in ('/', '&', '$'):

                    # Append any remaining patched variables
                    for v_name, v_val in grp_patch.items():
                        g_vars[v_name] = v_val
                        v_strs = nmls.var_strings(v_name, v_val)
                        for v_str in v_strs:
                            self.pfile.write('    {0}\n'.format(v_str))

                    # Append the grouplist to the namelist
                    if g_name in nmls:
                        g_update = nmls[g_name]

                        # Update to list of groups
                        if not isinstance(g_update, list):
                            g_update = [g_update]

                        g_update.append(g_vars)

                    else:
                        g_update = g_vars

                    nmls[g_name] = g_update

                    # Reset state
                    g_name, g_vars = None, None

            try:
                self.update_tokens()
            except StopIteration:
                break

        nml_file.close()
        if self.pfile:
            self.pfile.close()

        return nmls

    def parse_variable(self, parent, patch_nml=None):
        """Parse a variable and return its name and values."""

        if not patch_nml:
            patch_nml = NmlDict()

        v_name = self.prior_token
        v_values = []

        # Patch state
        patch_values = None
        write_token = v_name not in patch_nml

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

            if parent and v_name in parent:
                v_parent = parent[v_name]
            else:
                v_parent = []

            self.update_tokens()
            self.update_tokens()

            v_att, v_att_vals = self.parse_variable(v_parent)

            next_value = NmlDict()
            next_value[v_att] = v_att_vals
            append_value(v_values, next_value, v_idx)

        else:
            # Construct the variable array

            assert self.token == '='
            n_vals = None
            prior_ws_sep = ws_sep = False

            self.update_tokens()

            if v_name in patch_nml:
                patch_values = patch_nml.f90repr(patch_nml.pop(v_name))
                if not isinstance(patch_values, list):
                    patch_values = [patch_values]

                for p_val in patch_values:
                    self.pfile.write(p_val)

            # Add variables until next variable trigger
            while (self.token not in ('=', '(', '%') or
                   (self.prior_token, self.token) == ('=', '(')):

                # Check for repeated values
                if self.token == '*':
                    n_vals = self.parse_value(write_token)
                    assert isinstance(n_vals, int)
                    self.update_tokens(write_token)
                elif not n_vals:
                    n_vals = 1

                # First check for implicit null values
                if self.prior_token in ('=', '%', ','):
                    if (self.token in (',', '/', '&', '$') and
                            not (self.prior_token == ',' and
                                 self.token in ('/', '&', '$'))):
                        append_value(v_values, None, v_idx, n_vals)

                elif self.prior_token == '*':

                    if self.token not in ('/', '&', '$'):
                        self.update_tokens(write_token)

                    if (self.token == '=' or (self.token in ('/', '&', '$') and
                                              self.prior_token == '*')):
                        next_value = None
                    else:
                        next_value = self.parse_value(write_token)

                    append_value(v_values, next_value, v_idx, n_vals)

                else:
                    next_value = self.parse_value(write_token)

                    # Finished reading old value, we can again write tokens
                    write_token = True

                    # Check for escaped strings
                    if (v_values and isinstance(v_values[-1], str) and
                            isinstance(next_value, str) and not prior_ws_sep):

                        quote_char = self.prior_token[0]
                        v_values[-1] = quote_char.join([v_values[-1],
                                                        next_value])
                    else:
                        append_value(v_values, next_value, v_idx, n_vals)

                # Exit for end of nml group (/, &, $) or null broadcast (=)
                if self.token in ('/', '&', '$', '='):
                    break
                else:
                    prior_ws_sep = ws_sep
                    ws_sep = self.update_tokens(write_token)

        if patch_values:
            v_values = patch_values

        if not v_idx:
            v_values = delist(v_values)

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
                elif self.token not in (',', ')'):
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

        if self.token not in (',', ')'):
            raise ValueError('{0} index did not terminate '
                             'correctly.'.format(v_name))

        idx_triplet = (i_start, i_end, i_stride)
        v_indices.append((idx_triplet))
        self.update_tokens()

        return v_indices

    def parse_value(self, write_token=True):
        """Convert string repr of Fortran type to equivalent Python type."""
        v_str = self.prior_token

        # Construct the complex string
        if v_str == '(':
            v_re = self.token

            self.update_tokens(write_token)
            assert self.token == ','

            self.update_tokens(write_token)
            v_im = self.token

            self.update_tokens(write_token)
            assert self.token == ')'

            self.update_tokens(write_token)
            v_str = '({0}, {1})'.format(v_re, v_im)

        recast_funcs = [int, pyfloat, pycomplex, pybool, pystr]

        for f90type in recast_funcs:
            try:
                value = f90type(v_str)
                return value
            except ValueError:
                continue

    def update_tokens(self, write_token=True):
        """Update tokens to the next available values."""

        ws_sep = False
        next_token = next(self.tokens)

        if self.pfile and write_token:
            self.pfile.write(self.token)

        # Commas between values are interpreted as whitespace
        if self.token == ',':
            ws_sep = True

        while next_token in tuple(whitespace + '!'):

            if self.pfile:
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
    """Merge two lists or dicts into a single element."""

    if isinstance(src, dict) and isinstance(new, dict):
        return merge_dicts(src, new)
    else:
        if not isinstance(src, list):
            src = [src]
        if not isinstance(new, list):
            new = [new]

        return merge_lists(src, new)


def merge_lists(src, new):
    """Update a value list with a list of new or updated values."""

    l_min, l_max = (src, new) if len(src) < len(new) else (new, src)

    l_min.extend(None for i in range(len(l_min), len(l_max)))

    for i, val in enumerate(new):
        if isinstance(val, dict) and isinstance(src[i], dict):
            new[i] = merge_dicts(src[i], val)
        elif val is not None:
            new[i] = val
        else:
            new[i] = src[i]

    return new


def merge_dicts(src, patch):
    """Merge contents of dict `patch` into `src`."""

    for key in patch:
        if key in src:
            if isinstance(src[key], dict) and isinstance(patch[key], dict):
                merge_dicts(src[key], patch[key])
            else:
                src[key] = merge_values(src[key], patch[key])
        else:
            src[key] = patch[key]

    return src


def delist(values):
    """Reduce lists of zero or one elements to individual values."""
    assert isinstance(values, list)

    if not values:
        return None
    elif len(values) == 1:
        return values[0]
    else:
        return values
