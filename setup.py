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

try:
    from sphinx.setup_command import BuildDoc
    has_sphinx = True

    from distutils.command.build import build
    from distutils.command.build_py import build_py
    from distutils.command.install_data import install_data
except ImportError:
    has_sphinx = False

import tests.test_f90nml

# Project details
project_name = 'f90nml'
project_version = __import__(project_name).__version__
project_readme_fname = 'README.rst'
project_scripts = [os.path.join('bin', f) for f in os.listdir('bin')]


# The method below is largely based on Kentaro Wada's implementation in the
# wstools package.
# Reference: https://github.com/vcstools/wstool/blob/master/setup.py
#    commit: 8523f7fbe5e0690f0deb785ce54186b41358e31f

# NOTE: setuptools will not explicitly install data and instead packs it inside
# the egg.  While this is generally a good practice for modules which rely on
# user data, it makes it impossible to install things like documentation
# outside of the python space.
#
# We get around this by issuing a direct `install_data` command to distutils
# rather than relying on setuptools to install the data into its egg.

# TODO: Should probably also disable the install_data copy to the egg...


# Generate the man page if present
data_files = []
cmd_class = {}
if has_sphinx:
    # Create manpage build rule
    class ProjectBuildMan(BuildDoc):
        def initialize_options(self):
            BuildDoc.initialize_options(self)
            self.builder = 'man'

    # Include build_man into the main builds
    class ProjectBuild(build):
        def run(self):
            self.run_command('build_man')
            self.run_command('install_data')
            build.run(self)

    class ProjectBuildPy(build_py):
        def run(self):
            self.run_command('build_man')
            self.run_command('install_data')
            build_py.run(self)

    # Tabulate the builds
    cmd_class['build'] = ProjectBuild
    cmd_class['build_py'] = ProjectBuildPy
    cmd_class['build_man'] = ProjectBuildMan

    # Try to determine an appropriate man path
    if os.path.isdir(os.path.join(sys.prefix, 'share')):
        man_root = 'share'
    else:
        man_root = ''


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

cmd_class['test'] = ProjectTest


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

    data_files=data_files,
    cmdclass=cmd_class,

    classifiers = [
        'Development Status :: 4 - Beta',
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
        'Topic :: Utilities',
    ]
)
