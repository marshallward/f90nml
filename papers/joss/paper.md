---
title: 'f90nml - A Python module for Fortran namelists'
tags:
    - fortran
    - namelist
    - python
authors:
    - name: Marshall L. Ward
      orcid: 0000-0002-4944-7431
      affiliations: '1, 2'
affiliations:
    - name: NOAA Geophysical Fluid Dynamics Laboratory, Princeton, NJ, USA
      index: 1
    - name: National Computational Infrastructure, Canberra, Australia
      index: 2
date: 22 May 2019
---

# Summary

F90nml is a Python module used for importing, manipulating, and writing Fortran
namelist files.  The primary use case is to read a namelist variable into a
`Namelist` data structure, which behaves similarly to the intrinsic `dict`
type.  The content can be read and modified using standard Python methods, and
can be saved as a formatted namelist file.

Basic features include support for all intrinsic data types, as well as
user-defined types and multidimensional arrays.  User-defined types are
interpreted as hierarchical tree of `Namelists`\s.  Multidimensional arrays
are saved as nested lists of lists, with the most innermost lists corresponding
to the first dimensional index.  This reverses the index order in Python, but
corresponds to the usual ordering in memory.

F90nml also includes a `patch` feature, which allows one to modify the values
of an existing namelist while retaining its comments or existing formatting.
There is some limited ability to add or remove values when patching.

Because data type is set at runtime in the executable and is not specified in
the namelist, the data type of each value must be inferred, usually based on
the strictest interpretation of the value.  Weak typing rules within namelists,
such as the optional use of string delimiters or the rules for interpreting
logical values, can lead to further ambiguity, including across compilers, and
various control flags are provided to manage such behavior.  In most cases, an
ambiguous value will fall back to interpretation as a string.

Another limitation of the namelist format is the use of a arbitrary start index
in a Fortran array, which may be used at runtime but not specified in the
namelist.  For this reason, arrays are assumed to begin at the lowest explicit
index which exists in the namelist, which is stored as metadata.  For example,
if we parse the namelist below:

    &a_nml
       x(3:4) = 1.0, 1.1
       x(6:7) = 1.2, 1.3
    /

then it would be saved internally as the following 0-based Python list:

    nml = {
        'a_nml': {
            'x': [1.0, 1.1, None, 1.2, 1.3]
         }
         '_start_index': {'x': 3}
    }

When index is unspecified, then the index is left unspecified within the
`Namelist`, although ordering remains 0-based within the Python environment.
Additional control flags are also provided to control the start index.

F90nml also provides the following additional features:

- A command line tool for working in a shell environment

- Lossless conversion between `Namelist` and `dict` types

- Support for legacy Fortran namelist formats

- Conversion between JSON and YAML output

- Automated, configurable output formatting

The module is supported by an extensive test suite with a very high level of
code coverage, ensuring compatibility of existing namelists over future
releases.

This project is sustained by the feedback of its users, and continues to
benefit from contributions from its userbase, for which the author is immensely
grateful.
