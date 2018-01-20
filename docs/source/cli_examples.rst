.. highlight:: none

The examples below use the namelist file ``config.nml`` with the following
data.
::

  &config_nml
  input = 'wind.nc'
  steps = 864
  layout = 8, 16      ! (X, Y)
  visc = 1e-4         ! m2 s-1
  use_biharmonic = .false.
  /

To display the formatted output of a namelist::

   $ f90nml config.nml

::

   &config_nml
       input = 'wind.nc'
       steps = 864
       layout = 8, 16
       visc = 0.0001
       use_biharmonic = .false.
   /

To modify one of the values or add a new variable::

   $ f90nml -g config_nml -v steps=432 config.nml

::

   &config_nml
       input = 'wind.nc'
       steps = 432
       layout = 8, 16
       visc = 0.0001
       use_biharmonic = .false.
   /

Multiple variables can be set with separate flags or separated by commas::

   $ f90nml -g config_nml -v steps=432,date='19960101' config.nml

::

   $ f90nml -g config_nml -v steps=432 -v date='19960101' config.nml

::

   &config_nml
       input = 'wind.nc'
       steps = 432
       layout = 8, 16
       visc = 0.0001
       use_biharmonic = .false.
       date = 19960101
   /

Spaces should not be used when assigning values.

When the namelist group is unspecified, the first group is assumed::

   $ f90nml -v steps=432 config.nml

::

   f90nml: warning: Assuming variables are in group 'config_nml'.
   &config_nml
       input = 'wind.nc'
       steps = 432
       layout = 8, 16
       visc = 0.0001
       use_biharmonic = .false.
   /

To save the modified namelist to a new file, say ``out.nml``::

   $ f90nml -v steps=432 config.nml out.nml

To patch the existing file and preserve comments::

   $ f90nml -g config_nml -v steps=432 -p config.nml

::

   &config_nml
   input = 'wind.nc'
   steps = 432
   layout = 8, 16      ! (X, Y)
   visc = 1e-4         ! m2 s-1
   use_biharmonic = .false.
   /

To convert the output to JSON format::

   $ f90nml -g config_nml -v steps=432 config.nml -f json

::

   {
       "config_nml": {
           "input": "wind.nc",
           "steps": 432,
           "layout": [
               8,
               16
           ],
           "visc": 0.0001,
           "use_biharmonic": false
       }
   }

Output format is also inferred from the output extension.
::

   $ f90nml -g config_nml -v steps=432 config.nml out.json

::

   $ f90nml -g config_nml -v steps=432 config.nml out.yaml

JSON and YAML can also act as input files.  Format is assumed by extension.
::

   $ f90nml out.json

::

   &config_nml
       input = 'wind.nc'
       layout = 8, 16
       steps = 864
       use_biharmonic = .false.
       visc = 0.0001
   /
