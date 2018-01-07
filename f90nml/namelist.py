"""Fortran namelist interface.

The ``Namelist`` is a representation of a Fortran namelist and its contents in
a Python environment.

:copyright: Copyright 2014 Marshall Ward, see AUTHORS for details.
:license: Apache License, Version 2.0, see LICENSE for details.
"""
from __future__ import print_function

import numbers
import os
try:
    from StringIO import StringIO   # Python 2.x
except ImportError:
    from io import StringIO         # Python 3.x
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
try:
    basestring          # Python 2.x
except NameError:
    basestring = str    # Python 3.x


class Namelist(OrderedDict):
    """Representation of Fortran namelist in a Python environment."""

    def __init__(self, *args, **kwds):
        """Create the Namelist object."""
        s_args = list(args)

        # If using (unordered) dict, then resort the keys for reproducibility
        if (args and not isinstance(args[0], OrderedDict) and
                isinstance(args[0], dict)):
            s_args[0] = sorted(args[0].items())

        super(Namelist, self).__init__(*s_args, **kwds)

        # Convert any internal dicts to Namelists
        for key, val in self.items():
            if isinstance(val, dict):
                self[key] = Namelist(val)

        # Update any metadata
        if '_complex' in self:
            for key in self['_complex']:
                if all(isinstance(v, list) for v in self[key]):
                    self[key] = [complex(*v) for v in self[key]]
                else:
                    self[key] = complex(*self[key])
            self.pop('_complex')

        # Vector starting index tracking
        if '_start_index' in self:
            self.start_index = self['_start_index']
            self.pop('_start_index')
        if args and isinstance(args[0], Namelist):
            self.start_index = args[0].start_index
        else:
            self.start_index = {}

        # Formatting properties
        self._colwidth = 72
        self._indent = 4 * ' '
        self._end_comma = False
        self._uppercase = False
        self._floatformat = ''
        self._logical_repr = {False: '.false.', True: '.true.'}

        # Namelist group spacing flag
        self._newline = False

    def __contains__(self, key):
        return super(Namelist, self).__contains__(key.lower())

    def __delitem__(self, key):
        return super(Namelist, self).__delitem__(key.lower())

    def __getitem__(self, key):
        return super(Namelist, self).__getitem__(key.lower())

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, Namelist):
            value = Namelist(value)
        super(Namelist, self).__setitem__(key.lower(), value)

    def __str__(self):
        output = StringIO()
        if all(isinstance(v, Namelist) for v in self.values()):
            self.writestream(output)
        else:
            print(repr(self), file=output)

        nml_string = output.getvalue().rstrip()
        output.close()
        return nml_string

    # Format configuration

    # Column width
    @property
    def colwidth(self):
        """Maximum number of characters per line of the namelist file.

        Tokens longer than ``colwidth`` are allowed to extend past this limit
        (Default: 72).
        """
        return self._colwidth

    @colwidth.setter
    def colwidth(self, width):
        """Validate and set the column width."""
        if isinstance(width, int):
            if width >= 0:
                self._colwidth = width
            else:
                raise ValueError('Column width must be nonnegative.')
        else:
            raise TypeError('Column width must be a nonnegative integer.')

    @property
    def indent(self):
        r"""Whitespace indentation count.

        This can be set to an integer, denoting the number of spaces, or to an
        explicit whitespace character, such as a tab (``\t``)  (Default: 4).
        """
        return self._indent

    @indent.setter
    def indent(self, value):
        """Validate and set the indent width, either as an explicit whitespace
        string or by the number of whitespace characters.
        """
        # Explicit indent setting
        if isinstance(value, str):
            if value.isspace():
                self._indent = value
            else:
                raise ValueError('String indentation can only contain '
                                 'whitespace.')

        # Set indent width
        elif isinstance(value, int):
            if value >= 0:
                self._indent = value * ' '
            else:
                raise ValueError('Indentation spacing must be nonnegative.')

        else:
            raise TypeError('Indentation must be specified by string or space '
                            'width.')

    @property
    def end_comma(self):
        """Return True if entries are terminated with commas."""
        return self._end_comma

    @end_comma.setter
    def end_comma(self, value):
        """Validate and set the comma termination flag."""
        if not isinstance(value, bool):
            raise TypeError('end_comma attribute must be a logical type.')
        self._end_comma = value

    # Uppercase
    @property
    def uppercase(self):
        """Return True if names are displayed in upper case."""
        return self._uppercase

    @uppercase.setter
    def uppercase(self, value):
        """Validate and set the upper case flag."""
        if not isinstance(value, bool):
            raise TypeError('uppercase attribute must be a logical type.')
        self._uppercase = value

    # Float format
    @property
    def floatformat(self):
        """Return the current floating point format code."""
        return self._floatformat

    @floatformat.setter
    def floatformat(self, value):
        """Validate and set the upper case flag."""
        if isinstance(value, str):
            # Duck-test the format string; raise ValueError on fail
            '{0:{1}}'.format(1.23, value)

            self._floatformat = value
        else:
            raise TypeError('Floating point format code must be a string.')

    # Logical representation
    # NOTE: This presumes that bools and ints are identical as dict keys
    @property
    def logical_repr(self):
        """String representation of logical values ``False`` and ``True``.

        The properties ``true_repr`` and ``false_repr`` are also provided as
        interfaces to the ``logical_repr`` tuple
        (Default: ``.false., .true.``).
        """
        return self._logical_repr

    @logical_repr.setter
    def logical_repr(self, value):
        """Set the namelist representations of logical values."""

        if not any(isinstance(value, t) for t in (list, tuple)):
            raise TypeError("Logical representation must be a tuple with "
                            "a valid true and false value.")
        if not len(value) == 2:
            raise ValueError("List must contain two values.")

        self.false_repr = value[0]
        self.true_repr = value[1]

    @property
    def true_repr(self):
        """Return the namelist representation of logical true."""
        return self._logical_repr[1]

    @true_repr.setter
    def true_repr(self, value):
        """Validate and set the logical true representation."""
        if isinstance(value, str):
            if not (value.lower().startswith('t') or
                    value.lower().startswith('.t')):
                raise ValueError("Logical true representation must start with "
                                 "'T' or '.T'.")
            else:
                self._logical_repr[1] = value
        else:
            raise TypeError('Logical true representation must be a string.')

    @property
    def false_repr(self):
        """Return the namelist representation of logical false."""
        return self._logical_repr[0]

    @false_repr.setter
    def false_repr(self, value):
        """Validate and set the logical false representation."""
        if isinstance(value, str):
            if not (value.lower().startswith('f') or
                    value.lower().startswith('.f')):
                raise ValueError("Logical false representation must start "
                                 "with 'F' or '.F'.")
            else:
                self._logical_repr[0] = value
        else:
            raise TypeError('Logical false representation must be a string.')

    # File output

    def write(self, nml_path, force=False, sort=False):
        """Write Namelist to a Fortran 90 namelist file."""

        nml_is_file = hasattr(nml_path, 'read')
        if not force and not nml_is_file and os.path.isfile(nml_path):
            raise IOError('File {0} already exists.'.format(nml_path))

        nml_file = nml_path if nml_is_file else open(nml_path, 'w')
        try:
            self.writestream(nml_file, sort)
        finally:
            if not nml_is_file:
                nml_file.close()

    def patch(self, nml_patch):
        """Update the namelist from another partial or full namelist.

        This is different from `Namelist.update` as it does not replace
        namelist sections, instead it performs an update on the section."""
        for sec in nml_patch:
            if sec not in self:
                self[sec] = Namelist()
            self[sec].update(nml_patch[sec])

    def writestream(self, nml_file, sort=False):
        """Output Namelist to a streamable file object."""

        # Reset newline flag
        self._newline = False

        if sort:
            sel = Namelist(sorted(self.items(), key=lambda t: t[0]))
        else:
            sel = self

        for grp_name, grp_vars in sel.items():
            # Check for repeated namelist records (saved as lists)
            if isinstance(grp_vars, list):
                for g_vars in grp_vars:
                    self.write_nmlgrp(grp_name, g_vars, nml_file, sort)
            else:
                self.write_nmlgrp(grp_name, grp_vars, nml_file, sort)

    def write_nmlgrp(self, grp_name, grp_vars, nml_file, sort=False):
        """Write namelist group to target file."""

        if self._newline:
            print(file=nml_file)
        self._newline = True

        if self.uppercase:
            grp_name = grp_name.upper()

        if sort:
            grp_vars = Namelist(sorted(grp_vars.items(), key=lambda t: t[0]))

        print('&{0}'.format(grp_name), file=nml_file)

        for v_name, v_val in grp_vars.items():

            v_start = grp_vars.start_index.get(v_name, None)

            for v_str in self.var_strings(v_name, v_val, v_start=v_start):
                nml_line = self.indent + '{0}'.format(v_str)
                print(nml_line, file=nml_file)

        print('/', file=nml_file)

    def var_strings(self, v_name, v_values, v_idx=None, v_start=None):
        """Convert namelist variable to list of fixed-width strings."""

        if self.uppercase:
            v_name = v_name.upper()

        var_strs = []

        # Parse a multidimensional array
        if (isinstance(v_values, list) and
                any(isinstance(v, list) for v in v_values) and
                all((isinstance(v, list) or v is None) for v in v_values)):

            if not v_idx:
                v_idx = []

            i_s = v_start[::-1][len(v_idx)]

            # FIXME: We incorrectly assume 1-based indexing if it is
            # unspecified.  This is necessary because our output method always
            # separates the outer axes to one per line.  But we cannot do this
            # if we don't know the first index (which we are no longer assuming
            # to be 1-based elsewhere).  Unfortunately, the solution needs a
            # rethink of multidimensional output.

            # NOTE: Fixing this would also clean up the output of todict(),
            # which is now incorrectly documenting unspecified indices as 1.

            # For now, we will assume 1-based indexing here, just to keep
            # things working smoothly.
            if i_s is None:
                i_s = 1

            for idx, val in enumerate(v_values, start=i_s):
                v_idx_new = v_idx + [idx]
                v_strs = self.var_strings(v_name, val, v_idx=v_idx_new,
                                          v_start=v_start)
                var_strs.extend(v_strs)

        # Parse derived type contents
        elif isinstance(v_values, dict):
            for f_name, f_vals in v_values.items():
                v_title = '%'.join([v_name, f_name])

                v_start_new = v_values.start_index.get(f_name, None)

                v_strs = self.var_strings(v_title, f_vals, v_start=v_start_new)
                var_strs.extend(v_strs)

        # Parse an array of derived types
        elif (isinstance(v_values, list) and
              any(isinstance(v, dict) for v in v_values) and
              all((isinstance(v, dict) or v is None) for v in v_values)):

            if not v_idx:
                v_idx = []

            i_s = v_start[::-1][len(v_idx)]
            for idx, val in enumerate(v_values, start=i_s):

                # Skip any empty elements in a list of derived types
                if val is None:
                    continue

                v_title = v_name + '({0})'.format(idx)

                v_strs = self.var_strings(v_title, val)
                var_strs.extend(v_strs)

        else:
            if not isinstance(v_values, list):
                v_values = [v_values]

            # Print the index range

            # TODO: Include a check for len(v_values) to determine if vector
            if v_idx or v_start:
                v_idx_repr = '('

                if v_start:
                    i_s = v_start[0]

                    if i_s is None:
                        v_idx_repr += ':'

                    else:
                        i_e = i_s + len(v_values) - 1

                        if i_s == i_e:
                            v_idx_repr += '{0}'.format(i_s)
                        else:
                            v_idx_repr += '{0}:{1}'.format(i_s, i_e)

                # NOTE: The block below is never called!
                # We don't write the empty index if none was provided.
                # But maybe someday we might want to add this option.

                # else:
                #     v_idx_repr += ':'

                if v_idx:
                    v_idx_repr += ', '
                    v_idx_repr += ', '.join(str(i) for i in v_idx[::-1])

                v_idx_repr += ')'

            else:
                v_idx_repr = ''

            # Split output across multiple lines (if necessary)

            val_strs = []

            val_line = ''
            for v_val in v_values:

                v_header = v_name + v_idx_repr + ' = '
                # Increase column width if the header exceeds this value
                if len(self.indent + v_header) >= self.colwidth:
                    colwidth = len(self.indent + v_header) + 1
                else:
                    colwidth = self.colwidth

                v_width = colwidth - len(self.indent + v_header)

                if len(val_line) < v_width:
                    val_line += self.f90repr(v_val) + ', '

                if len(val_line) >= v_width:
                    val_strs.append(val_line.rstrip())
                    val_line = ''

            # Append any remaining values
            if val_line:
                val_strs.append(val_line.rstrip())

            if val_strs:
                if self.end_comma or v_values[-1] is None:
                    pass
                else:
                    val_strs[-1] = val_strs[-1][:-1]

            # Complete the set of values
            if val_strs:
                var_strs.append('{0}{1} = {2}'
                                ''.format(v_name, v_idx_repr,
                                          val_strs[0]).strip())

                for v_str in val_strs[1:]:
                    var_strs.append(' ' * len(v_header) + v_str)

        return var_strs

    def todict(self, decomplex=False):
        """Return a dict equivalent to the namelist."""
        # NOTE: Since namelists cannot start with `_`, we use these keys to
        # include metadata.

        # TODO: Preserve ordering
        nmldict = OrderedDict(self)

        # Search for namelists within the namelist
        # TODO: Move repeated stuff to new functions
        for key, value in self.items():
            if isinstance(value, Namelist):
                nmldict[key] = value.todict(decomplex)

            elif isinstance(value, complex) and decomplex:
                nmldict[key] = [value.real, value.imag]
                try:
                    nmldict['_complex'].append(key)
                except KeyError:
                    nmldict['_complex'] = [key]

            elif isinstance(value, list):
                complex_list = False
                for idx, entry in enumerate(value):
                    if isinstance(entry, Namelist):
                        nmldict[key][idx] = entry.todict(decomplex)

                    elif isinstance(entry, complex) and decomplex:
                        nmldict[key][idx] = [entry.real, entry.imag]
                        complex_list = True

                if complex_list:
                    try:
                        nmldict['_complex'].append(key)
                    except KeyError:
                        nmldict['_complex'] = [key]

        # Append the start index if present
        if self.start_index:
            start_index = {}
            for key, value in self.start_index.items():
                # NOTE: This only supports default values of 1
                if all(v != 1 for v in value):
                    start_index[key] = value

            if start_index:
                nmldict['_start_index'] = start_index

        return nmldict

    def f90repr(self, value):
        """Convert primitive Python types to equivalent Fortran strings."""

        if isinstance(value, bool):
            return self.f90bool(value)
        elif isinstance(value, numbers.Integral):
            return self.f90int(value)
        elif isinstance(value, numbers.Real):
            return self.f90float(value)
        elif isinstance(value, numbers.Complex):
            return self.f90complex(value)
        elif isinstance(value, basestring):
            return self.f90str(value)
        elif value is None:
            return ''
        else:
            raise ValueError('Type {0} of {1} cannot be converted to a Fortran'
                             ' type.'.format(type(value), value))

    def f90bool(self, value):
        """Return a Fortran 90 representation of a logical value."""
        return self.logical_repr[value]

    def f90int(self, value):
        """Return a Fortran 90 representation of an integer."""
        return str(value)

    def f90float(self, value):
        """Return a Fortran 90 representation of a floating point number."""
        return '{0:{fmt}}'.format(value, fmt=self.floatformat)

    def f90complex(self, value):
        """Return a Fortran 90 representation of a complex number."""
        return '({0:{fmt}}, {1:{fmt}})'.format(value.real, value.imag,
                                               fmt=self.floatformat)

    def f90str(self, value):
        """Return a Fortran 90 representation of a string."""

        # Replace Python quote escape sequence with Fortran
        result = repr(str(value)).replace("\\'", "''").replace('\\"', '""')

        # Un-escape the Python backslash escape sequence
        result = result.replace('\\\\', '\\')

        return result
