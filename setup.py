"""Installation script for f90nml.

Additional configuration settings are in ``setup.cfg``.

:copyright: Copyright 2014 Marshall Ward, see AUTHORS for details.
:license: Apache License, Version 2.0, see LICENSE for details.
"""
import os
import sys
import tokenize

try:
    from setuptools import setup
    from setuptools import Command
except ImportError:
    from distutils.core import setup
    from distutils.core import Command

# Project details

project_name = 'f90nml'

# Parse version.py and get version number
with open(os.path.join(project_name, 'version.py'), 'rb') as version_py:
    tokens = tokenize.tokenize(version_py.readline)

    for tok_type, tok_str, _, _, _ in tokens:
        if tok_type == tokenize.NAME and tok_str == '__version__':
            next_type, next_str, _, _, _ = next(tokens)

            if next_type != tokenize.OP or next_str != '=':
                raise RuntimeError("Expected '=' after __version__.")

            next_type, next_str, _, _, _ = next(tokens)

            if next_type != tokenize.STRING:
                raise RuntimeError("__version__ is not a string.")

            project_version = eval(next_str)
            break


# Project setup
setup(name=project_name, version=project_version)
