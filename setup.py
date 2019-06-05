"""Installation script for f90nml.

Additional configuration settings are in ``setup.cfg``.

:copyright: Copyright 2014 Marshall Ward, see AUTHORS for details.
:license: Apache License, Version 2.0, see LICENSE for details.
"""
import os
import sys

try:
    from setuptools import setup
    from setuptools import Command
except ImportError:
    from distutils.core import setup
    from distutils.core import Command

import tests.test_f90nml

# Project details
project_name = 'f90nml'
project_version = __import__(project_name).__version__
project_readme_fname = 'README.rst'
project_scripts = [os.path.join('bin', f) for f in os.listdir('bin')]


# Test suite
class ProjectTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        unittest = tests.test_f90nml.unittest
        testcase = tests.test_f90nml.Test
        suite = unittest.TestLoader().loadTestsFromTestCase(testcase)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(not result.wasSuccessful())


# README
with open(project_readme_fname) as f:
    project_readme = f.read()


# Project setup
setup(
    name = project_name,
    version = project_version,
    description = 'Fortran 90 namelist parser',
    long_description = project_readme,
    author = 'Marshall Ward',
    author_email = 'f90nml@marshallward.org',
    url = 'http://github.com/marshallward/f90nml',

    packages = ['f90nml'],
    scripts=project_scripts,

    extras_require = {
        'yaml': ['PyYAML'],
    },

    cmdclass = {'test': ProjectTest},

    classifiers = [
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
