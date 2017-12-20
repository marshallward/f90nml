:orphan:

======
f90nml
======

SYNPOSIS
========

f90nml
   [-h] [--version] [--group GROUP] [--variable VARIABLE] [--patch]
   [--format FORMAT] [--output OUTPUT] [input] [output]


DESCRIPTION
===========

``f90nml`` is a command line tool for the reading, writing, and the general
manipulation of Fortran namelist files.


OPTIONS
=======

-g, --group GROUP
   specify namelist group to modify.  When absent, the first group is used

-v, --variable VARIABLE=VALUE
   specify the namelist variable to add or modify, followed by the new value

-p, --patch
   modify the existing namelist as a patch

-f, --format
   specify the output format (json, yaml, or nml)

-o, --output
   set the output filename.  When absent, output is send to standard output

-h, --help
   display this help and exit

--version
   output version information and exit
