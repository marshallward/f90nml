"""The f90nml namelist parser and tokenizer.

The ``Parser`` object converts the contents of a Fortran namelist into a
hierarchy of Python dicts containing equivalent intrinsic Python data types.

:copyright: Copyright 2014 Marshall Ward, see AUTHORS for details.
:license: Apache License, Version 2.0, see LICENSE for details.
"""
import copy
from string import whitespace

from f90nml.fpy import pyfloat, pycomplex, pybool, pystr
from f90nml.namelist import Namelist
from f90nml.findex import FIndex
from f90nml.tokenizer import Tokenizer


class Parser(object):
    """shlex-based Fortran namelist parser."""

    def __init__(self):
        """Create the parser object."""

        # Token management
        self.tokens = None
        self.token = None
        self.prior_token = None

        # Patching
        self.pfile = None

        # Control flags
        self._row_major = False
        self._strict_logical = True
        self.default_start_index = 1        # TODO: use a property
        self.global_start_index = None      # TODO: Property, vector index

        # Configuration
        self.comment_tokens = '!'

    @property
    def row_major(self):
        """Return true if multidimensional arrays are in row-major format."""
        return self._row_major

    @row_major.setter
    def row_major(self, value):
        """Validate and set row-major format for multidimensional arrays."""

        if value is not None:
            if not isinstance(value, bool):
                raise ValueError(
                    'f90nml: error: row_major must be a logical value.')
            else:
                self._row_major = value

    @property
    def strict_logical(self):
        """Return true for strict logical value parsing."""
        return self._strict_logical

    @strict_logical.setter
    def strict_logical(self, value):
        """Validate and set the strict logical flag."""

        if value is not None:
            if not isinstance(value, bool):
                raise ValueError(
                    'f90nml: error: strict_logical must be a logical value.')
            else:
                self._strict_logical = value

    def read(self, nml_fname, nml_patch_in=None, patch_fname=None):
        """Parse a Fortran namelist file and store the contents.

        >>> from f90nml.parser import Parser
        >>> parser = Parser()
        >>> data_nml = parser.read('data.nml')"""

        # For switching based on files versus paths
        nml_is_path = not hasattr(nml_fname, 'read')
        patch_is_path = not hasattr(patch_fname, 'read')

        # Convert patch data to a Namelist object
        if nml_patch_in:
            if not isinstance(nml_patch_in, dict):
                raise ValueError('Input patch must be a dict or a Namelist.')

            nml_patch = copy.deepcopy(Namelist(nml_patch_in))

            if not patch_fname and nml_is_path:
                patch_fname = nml_fname + '~'
            elif not patch_fname:
                raise ValueError('f90nml: error: No output file for patch.')
            elif nml_fname == patch_fname:
                raise ValueError('f90nml: error: Patch filepath cannot be the '
                                 'same as the original filepath.')
            if patch_is_path:
                self.pfile = open(patch_fname, 'w')
            else:
                self.pfile = patch_fname
        else:
            nml_patch = Namelist()

        try:
            nml_file = open(nml_fname, 'r') if nml_is_path else nml_fname
            try:
                return self.readstream(nml_file, nml_patch)

            # Close the files we opened on any exceptions within readstream
            finally:
                if nml_is_path:
                    nml_file.close()
        finally:
            if self.pfile and patch_is_path:
                self.pfile.close()

    def readstream(self, nml_file, nml_patch):
        """Parse an input stream containing a Fortran namelist."""

        tokenizer = Tokenizer()
        f90lex = []
        for line in nml_file:
            toks = tokenizer.parse(line)
            toks.append('\n')
            f90lex.extend(toks)

        self.tokens = iter(f90lex)

        nmls = Namelist()

        # Attempt to get first token; abort on empty file
        try:
            self.update_tokens(write_token=False)
        except StopIteration:
            return nmls

        # TODO: Replace "while True" with an update_token() iterator
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

            g_vars = Namelist()
            v_name = None

            # TODO: Edit `Namelist` to support case-insensitive `get` calls
            grp_patch = nml_patch.get(g_name.lower(), {})

            # Populate the namelist group
            while g_name:

                if self.token not in ('=', '%', '('):
                    self.update_tokens()

                # Set the next active variable
                if self.token in ('=', '(', '%'):

                    v_name, v_values = self.parse_variable(g_vars,
                                                           patch_nml=grp_patch)

                    if v_name in g_vars:
                        v_prior_values = g_vars[v_name]
                        v_values = merge_values(v_prior_values, v_values)

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

        return nmls

    def parse_variable(self, parent, patch_nml=None):
        """Parse a variable and return its name and values."""

        if not patch_nml:
            patch_nml = Namelist()

        v_name = self.prior_token
        v_values = []

        # Patch state
        patch_values = None

        # Derived type parent index (see notes below)
        dt_idx = None

        if self.token == '(':

            v_idx_bounds = self.parse_indices()
            v_idx = FIndex(v_idx_bounds, self.global_start_index)

            # Update starting index against namelist record
            if v_name.lower() in parent.start_index:
                p_idx = parent.start_index[v_name.lower()]

                for idx, pv in enumerate(zip(p_idx, v_idx.first)):
                    if all(i is None for i in pv):
                        i_first = None
                    else:
                        i_first = min(i for i in pv if i is not None)

                    v_idx.first[idx] = i_first

                # Resize vector based on starting index
                for i_p, i_v in zip(p_idx, v_idx.first):
                    if i_p is not None and i_v is not None and i_v < i_p:
                        pad = [None for _ in range(i_p - i_v)]
                        parent[v_name] = pad + parent[v_name]

            else:
                # If variable already existed without an index, then assume a
                #   1-based index
                # FIXME: Need to respect undefined `None` starting indexes?
                if v_name in parent:
                    v_idx.first = [self.default_start_index
                                   for _ in v_idx.first]

            parent.start_index[v_name.lower()] = v_idx.first

            self.update_tokens()

            # Derived type parent check
            # NOTE: This assumes single-dimension derived type vectors
            #       (which I think is the only case supported in Fortran)
            if self.token == '%':
                assert(v_idx_bounds[0][1] - v_idx_bounds[0][0] == 1)
                dt_idx = v_idx_bounds[0][0] - v_idx.first[0]

                # NOTE: This is the sensible play to call `parse_variable`
                # but not yet sure how to implement it, so we currently pass
                # along `dt_idx` to the `%` handler.

        else:
            v_idx = None

            # If indexed variable already exists, then re-index this new
            #   non-indexed variable using the global start index

            if v_name in parent.start_index:
                p_start = parent.start_index[v_name.lower()]
                v_start = [self.default_start_index for _ in p_start]

                # Resize vector based on new starting index
                for i_p, i_v in zip(p_start, v_start):
                    if i_v < i_p:
                        pad = [None for _ in range(i_p - i_v)]
                        parent[v_name] = pad + parent[v_name]

                parent.start_index[v_name.lower()] = v_start

        if self.token == '%':

            # Resolve the derived type

            # Check for value in patch
            v_patch_nml = None
            if v_name in patch_nml:
                v_patch_nml = patch_nml.pop(v_name.lower())

            if parent:
                vpar = parent.get(v_name.lower())
                if vpar and isinstance(vpar, list):
                    assert dt_idx is not None
                    try:
                        v_parent = vpar[dt_idx]
                    except IndexError:
                        v_parent = Namelist()
                elif vpar:
                    v_parent = vpar
                else:
                    v_parent = Namelist()
            else:
                v_parent = Namelist()
                parent[v_name] = v_parent

            self.update_tokens()
            self.update_tokens()

            v_att, v_att_vals = self.parse_variable(v_parent,
                                                    patch_nml=v_patch_nml)

            next_value = Namelist()
            next_value[v_att] = v_att_vals
            self.append_value(v_values, next_value, v_idx)

        else:
            # Construct the variable array

            assert self.token == '='
            n_vals = None

            self.update_tokens()

            # Check if value is in the namelist patch
            # TODO: Edit `Namelist` to support case-insensitive `pop` calls
            #       (Currently only a problem in PyPy2)
            if v_name in patch_nml:
                patch_values = patch_nml.pop(v_name.lower())

                if not isinstance(patch_values, list):
                    patch_values = [patch_values]

                p_idx = 0

            # Add variables until next variable trigger
            while (self.token not in ('=', '(', '%') or
                   (self.prior_token, self.token) == ('=', '(')):

                # Check for repeated values
                if self.token == '*':
                    n_vals = self.parse_value()
                    assert isinstance(n_vals, int)
                    self.update_tokens()
                elif not n_vals:
                    n_vals = 1

                # First check for implicit null values
                if self.prior_token in ('=', '%', ','):
                    if (self.token in (',', '/', '&', '$') and
                            not (self.prior_token == ',' and
                                 self.token in ('/', '&', '$'))):
                        self.append_value(v_values, None, v_idx, n_vals)

                elif self.prior_token == '*':

                    if self.token not in ('/', '&', '$'):
                        self.update_tokens()

                    if (self.token == '=' or (self.token in ('/', '&', '$') and
                                              self.prior_token == '*')):
                        next_value = None
                    else:
                        next_value = self.parse_value()

                    self.append_value(v_values, next_value, v_idx, n_vals)

                else:
                    next_value = self.parse_value()
                    self.append_value(v_values, next_value, v_idx, n_vals)

                # Reset default repeat factor for subsequent values
                n_vals = 1

                # Exit for end of nml group (/, &, $) or null broadcast (=)
                if self.token in ('/', '&', '$', '='):
                    break
                else:
                    if patch_values:
                        if (p_idx < len(patch_values) and
                                len(patch_values) > 0 and self.token != ','):
                            p_val = patch_values[p_idx]
                            p_repr = patch_nml.f90repr(patch_values[p_idx])
                            p_idx += 1
                            self.update_tokens(override=p_repr)
                            if isinstance(p_val, complex):
                                # Skip over the complex content
                                # NOTE: Assumes input and patch are complex
                                self.update_tokens(write_token=False)
                                self.update_tokens(write_token=False)
                                self.update_tokens(write_token=False)
                                self.update_tokens(write_token=False)

                        else:
                            # Skip any values beyond the patch size
                            skip = (p_idx >= len(patch_values))
                            self.update_tokens(patch_skip=skip)
                    else:
                        self.update_tokens()

        if patch_values:
            v_values = patch_values

        if not v_idx:
            v_values = delist(v_values)

        return v_name, v_values

    def parse_indices(self):
        """Parse a sequence of Fortran vector indices as a list of tuples."""

        v_name = self.prior_token
        v_indices = []

        while self.token in (',', '('):
            v_indices.append(self.parse_index(v_name))

        return v_indices

    def parse_index(self, v_name):
        """Parse Fortran vector indices into a tuple of Python indices."""

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
        return idx_triplet

    def parse_value(self, write_token=True, override=None):
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

            self.update_tokens(write_token, override)
            v_str = '({0}, {1})'.format(v_re, v_im)

        recast_funcs = [int, pyfloat, pycomplex, pybool, pystr]

        for f90type in recast_funcs:
            try:
                # Unclever hack.. integrate this better
                if f90type == pybool:
                    value = pybool(v_str, self.strict_logical)
                else:
                    value = f90type(v_str)
                return value
            except ValueError:
                continue

    def update_tokens(self, write_token=True, override=None, patch_skip=False):
        """Update tokens to the next available values."""

        next_token = next(self.tokens)

        patch_value = ''
        patch_tokens = ''

        if self.pfile and write_token:
            token = override if override else self.token
            patch_value += token

        while (next_token[0] in self.comment_tokens + whitespace):
            if self.pfile:
                if next_token[0] in self.comment_tokens:
                    while not next_token == '\n':
                        patch_tokens += next_token
                        next_token = next(self.tokens)
                patch_tokens += next_token

            # Several sections rely on StopIteration to terminate token search
            # If that occurs, dump the patched tokens immediately
            try:
                next_token = next(self.tokens)
            except StopIteration:
                if not patch_skip or next_token in ('=', '(', '%'):
                    patch_tokens = patch_value + patch_tokens

                if self.pfile:
                    self.pfile.write(patch_tokens)
                raise

        # Write patched values and whitespace + comments to file
        if not patch_skip or next_token in ('=', '(', '%'):
            patch_tokens = patch_value + patch_tokens

        if self.pfile:
            self.pfile.write(patch_tokens)

        # Update tokens, ignoring padding
        self.token, self.prior_token = next_token, self.token

    def append_value(self, v_values, next_value, v_idx=None, n_vals=1):
        """Update a list of parsed values with a new value."""

        for _ in range(n_vals):
            if v_idx:
                v_i = next(v_idx)
                v_s = [self.default_start_index if idx is None else idx
                       for idx in v_idx.first]

                if not self.row_major:
                    v_i = v_i[::-1]
                    v_s = v_s[::-1]

                # Multidimensional arrays
                v_tmp = v_values
                for (i_v, i_s) in zip(v_i[:-1], v_s[:-1]):
                    try:
                        v_tmp = v_tmp[i_v - i_s]
                    except IndexError:
                        size = len(v_tmp)
                        v_tmp.extend([] for _ in range(size, i_v - i_s + 1))
                        v_tmp = v_tmp[i_v - i_s]

                i_v, i_s = v_i[-1], v_s[-1]
                try:
                    v_tmp[i_v - i_s] = next_value
                except IndexError:
                    size = len(v_tmp)
                    v_tmp.extend(None for _ in range(size, i_v - i_s + 1))
                    v_tmp[i_v - i_s] = next_value
            else:
                v_values.append(next_value)


# Support functions

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
        elif isinstance(val, list) and isinstance(src[i], list):
            new[i] = merge_lists(src[i], val)
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
