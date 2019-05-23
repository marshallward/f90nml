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
    - name: Australian National University, Canberra, Australia
      index: 2
date: 22 May 2019
bibliography: paper.bib
---

Summary
=======

`f90nml` is a Python module used for importing, manipulating, and writing
Fortran namelist files [@ISO:2018:1539:1].  The primary use case for this
module is to read a namelist file via the `Parser` and save its contents into a
`Namelist` data structure, which is a case-insensitive subclass of a `dict`,
Python's intrinsic associative array.  The `Namelist` object can be read and
modified as a standard Python `dict`, and its contents can be saved as a
formatted namelist file.

Fortran continues to be a dominant programming language in high-performance
scientific computing [@SPECMPI2007:2010, @ClimateFortranDev:2014] and namelists
have been a part of the language for decades.  Namelists were an early method
of serializing numerical data into a human-readable format, although this has
become less practical as data sizes have increased.  In more recent times,
namelists have been more commonly used for runtime configuration [@MOM5:2012,
@WRF:2019, @QUANTUMESPRESSO:2009, @UM:2019].  Much of the work associated with
managing and documenting the runtime parameters over a large ensemble of runs
can in part be reduced to the parsing, modifying, and storing of namelists.

Python has been a dominant programming language in the sciences in recent years
[@PyAstro:2019], consistent with the overall trend across programming
[@PythonSO:2017], which has created a growing need for tools in Python which
can manage legacy data formats.  Given the importance of Fortran in both
historical and modern scientific computing, the ability to accurately read and
manipulate namelists offers the ability to both archive numerical results from
the past and to automate the configuration of future simulations.

An example namelist, such as the one shown below:
```
&config_nml
    input = 'wind.nc'
    steps = 864
    layout = 8, 16
    visc = 1.0e-4
    use_biharmonic = .false.
/
```
would be stored as a `Namelist` equivalent to the following `dict`:
```
nml = {
    'config_nml': {
        'input': 'wind.nc',
        'steps': 864,
        'layout': [8, 16],
        'visc': 0.0001,
        'use_biharmonic': False
    }
}
```
The module supports all intrinsic data types, as well as user-defined types and
multidimensional arrays.  User-defined types are interpreted as hierarchical
tree of `Namelist`s.  Multidimensional arrays are saved as nested lists of
lists, with the most innermost lists corresponding to the first dimensional
index.  This reverses the index order in Python, but corresponds to the usual
ordering in memory.

`f90nml` also includes a `patch` feature, which allows one to modify the values
of an existing namelist while retaining its comments or existing whitespace
formatting.  There is some limited ability to add or remove values during
patching.

Because a value's data type is assigned by the executable at runtime and is not
specified in the namelist, the data type of each value must be inferred by the
module, usually based on the strictest interpretation of the value.  Weak
typing rules within namelists, such as the optional use of string delimiters or
the multiple representations of logical values, can lead to further ambiguity.
`f90nml` provides various control flags to manage these cases.  A truly
ambiguous value will typically be intepreted as a literal string, rather than
raise an error.

Another limitation of the namelist format is the use of a arbitrary start index
in a Fortran array, which may be used at runtime but not specified in the
namelist.  For this reason, arrays are assumed to begin at the lowest explicit
index which is defined in the namelist, and is stored as metadata.  For
example, if we parse the namelist below:
```
    &a_nml
       x(3:4) = 1.0, 1.1
       x(6:7) = 1.2, 1.3
    /
```
then it would be saved internally as the following 0-based Python list:
```
    nml = {
        'a_nml': {
            'x': [1.0, 1.1, None, 1.2, 1.3]
         }
         '_start_index': {'x': 3}
    }
```
If the start index is unspecified, then the index is also unspecified within
the `Namelist`, although ordering remains 0-based within the Python
environment.  Additional control flags are also provided to control the start
index.

`f90nml` also provides the following additional features:

-   A command line tool for working in a shell environment
-   Lossless conversion between `Namelist` and `dict` types
-   Support for legacy Fortran namelist formats
-   Conversion between JSON and YAML output
-   Automated, configurable output formatting
-   Handling of repeated groups within a namelist

The module is supported by an extensive test suite with a very high level of
code coverage, ensuring compatibility of existing namelists over future
releases.


Acknowledgements
================

Development of `f90nml` has been ongoing for several years, and was created to
support research activites at the Australian National University as part of the
Australian Centre of Excellence in Climate System Science (ARCCSS).

This project is sustained by the feedback from its users, and continues to
benefit from contributions from its userbase, for which the author is immensely
grateful.


References
==========
