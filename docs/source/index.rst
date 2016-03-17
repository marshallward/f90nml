==============================================================
``f90nml`` -- A Fortran namelist parser, generator, and editor
==============================================================

A Python module for parsing Fortran namelist files

.. image:: https://travis-ci.org/marshallward/f90nml.svg?branch=master
    :target: https://travis-ci.org/marshallward/f90nml

.. image:: https://coveralls.io/repos/marshallward/f90nml/badge.png?branch=master
   :target: https://coveralls.io/r/marshallward/f90nml?branch=master


About ``f90nml``
================

``f90nml`` is a Python module that provides a simple interface for the reading,
writing, and the general manipulation of Fortran namelist files.

A namelist file is parsed and converted into an ``Namelist`` object, which
behaves like a standard Python ``dict``.  Values are converted from Fortran
data types to equivalent primitive Python types.


Quick usage guide
=================

To read a namelist file ``sample.nml`` which contains the following namelists:

.. code:: fortran

   &config_nml
      input = 'wind.nc'
      steps = 864
      layout = 8, 16
      visc = 1e-4
      use_biharmonic = .false.
   /

we would use the following script:

.. code:: python

   import f90nml
   nml = f90nml.read('sample.nml')

which would would point ``nml`` to the following ``dict``:

.. code:: python

   nml = {'config_nml':
            {'input': 'wind.nc',
             'steps': 864,
             'layout': [8, 16],
             'visc': 0.0001
             'use_biharmonic': False
            }
         }

File objects can also be used as inputs:

.. code:: python

   with open('sample.nml') as nml_file:
       nml = f90nml.read(nml_file)

To modify one of the values, say ``steps``, and save the output, just
manipulate the ``nml`` contents and write to disk using the ``write`` function:

.. code:: python

   nml['config_nml']['steps'] = 432
   nml.write('new_sample.nml')

Namelists can also be saved to file objects:

.. code:: python

   with open('target.nml') as nml_file:
      nml.write(nml_file)

To modify a namelist but preserve its comments and formatting, create a
namelist (or ``dict``) patch and apply it to a target file using the ``patch``
function:

.. code:: python

   patch_nml = {'config_nml': {'visc': 1e-6}}
   f90nml.patch('sample.nml', patch_nml, 'new_sample.nml')


Installation
============

``f90nml`` is available on PyPI and can be installed via pip::

   $ pip install f90nml

It is also available on Arch Linux via the AUR::

   $ git clone https://aur.archlinux.org/python-f90nml.git
   $ cd python-f90nml
   $ makepkg -sri

``f90nml`` is not yet available on other Linux distributions.

The latest version of ``f90nml`` can be installed from source::

   $ git clone https://github.com/marshallward/f90nml.git
   $ cd f90nml
   $ python setup.py install

Users without install privileges can append the ``--user`` flag to
``setup.py``::

   $ python setup.py --user install


Basic Usage
===========

.. autofunction:: f90nml.read

.. autofunction:: f90nml.write

.. autofunction:: f90nml.patch


Notes
=====

Data types
----------

Fortran namelists do not contain any information about data type, which is
determined by the target variables of the Fortran executable.  ``f90nml``
infers the data type based on the value, but not all cases can be explicitly
resolved.

``f90nml`` tests values as one of each data type in the order listed below:

* Integer

* Floating point

* Complex floating point

* Logical (boolean)

* String

Strings acts as a fallback type.  If a value cannot be matched to any other
value, then it is interpreted as a string.

In order to get the best results from ``f90nml``, it is best to follow these
guidelines:

* All strings should be enclosed by string delimiters (``'``, ``"``).

* Floating point values should use decimals (``.``) or `E notation`_.

* Array indices should be explicit

* Array values should be separated by commas (``,``)

.. _E notation: https://en.wikipedia.org/wiki/Scientific_notation#E_notation


Derived Types
-------------

User-defined types are saved as a nested hierarcy of ``dict``\ s.  For example,
the following namelist

.. code:: fortran

   &dtype_nml
      a%b%c = 1
   /

would be saved as the following ``Namelist``:

.. code:: python

   nml = {'dtype_nml':
            {'a':
               {'b':
                  {'c': 1}
               }
            }
         }


Output formatting
-----------------

The output format of ``f90nml.write`` can be altered by modifying the
properties of the ``Namelist`` object.  The properties for a sample namelist
``nml`` are shown below.

``nml.colwidth`` (Default: 72)
   Maximum number of characters per line of the namelist file.  Tokens longer
   than ``colwidth`` are allowed to extend past this limit.

``nml.indent`` (Default: 4)
   Whitespace indentation.  This can be set to an integer, denoting the number
   of spaces, or to an explicit whitespace character, such as a tab (``\t``).

``nml.end_comma`` (Default: ``False``)
   Append a comma (``,``) to the end of each namelist entry.

``nml.uppercase`` (Default: ``False``)
   Display namelist and variable names in uppercase.

``nml.floatformat`` (Default: ``None``)
   Specify the floating point output format, as expected by Python ``format``
   function.

``nml.logical_repr`` (Default: ``.false., .true.``)
   String representation of logical values ``False`` and ``True``.  The
   properties ``true_repr`` and ``false_repr`` are also provided as interfaces
   to the ``logical_repr`` tuple.


Comment tokens
--------------

Some Fortran programs will introduce alternative comment tokens (e.g. ``#``)
for internal preprocessing.

If you need to support these tokens, create a ``Parser`` object and set the
comment token as follows:

.. code:: python

   parser = f90nml.Parser()
   parser.comment_tokens += '#'
   nml = Parser.read('sample.nml')

Be aware that this is non-standard Fortran and could mangle any strings using
the '#' characters.  Characters inside string delimiters should be protected.


Classes
=======

.. autoclass:: f90nml.parser.Parser

.. autoclass:: f90nml.namelist.Namelist

.. autoclass:: f90nml.findex.FIndex


Licensing
=========

``f90nml`` is distributed under the `Apache 2.0 License`_.

.. _Apache 2.0 License:
    http://www.apache.org/licenses/LICENSE-2.0.txt

Contact
=======

Marshall Ward <f90nml@marshallward.org>
