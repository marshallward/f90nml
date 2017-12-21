-g GROUP, --group GROUP    specify namelist group to modify.  When absent, the first
                           group is used

-v EXPR, --variable EXPR   specify the namelist variable to add or modify, followed
                           by the new value.  Expressions are of the form
                           "VARIABLE=VALUE"

-p, --patch    modify the existing namelist as a patch

-f, --format   specify the output format (json, yaml, or nml)

-o, --output   set the output filename.  When absent, output is send to
               standard output

-h, --help     display this help and exit

--version      output version information and exit
