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

project_readme_fname = 'README.rst'
project_scripts = [os.path.join('bin', f) for f in os.listdir('bin')]


# README
with open(project_readme_fname) as f:
    project_readme = f.read()


# Project setup
setup(
    name=project_name,
    version=project_version,
    description='Fortran 90 namelist parser',
    long_description=project_readme,
    author='Marshall Ward',
    author_email='f90nml@marshallward.org',
    url='http://github.com/marshallward/f90nml',

    packages=['f90nml'],
    scripts=project_scripts,

    extras_require={
        'yaml': ['PyYAML'],
    },

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
    ]
)
