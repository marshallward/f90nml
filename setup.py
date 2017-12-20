"""Installation script for f90nml.

Additional configuration settings are in ``setup.cfg``.

:copyright: Copyright 2014 Marshall Ward, see AUTHORS for details.
:license: Apache License, Version 2.0, see LICENSE for details.
"""
import os
import sys
try:
    # NOTE: setuptools will not install manpages, probably for good reason
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    from sphinx.setup_command import BuildDoc
    has_sphinx = True

    from distutils.command.build import build
    from distutils.command.build_py import build_py
except ImportError:
    has_sphinx = False


# NOTE: I am disabling man page installation for now, since the current method
#       does not work for setuptools, and is still too Unix-specific.
#       We may need to make install_man a wholly separate command.
install_man_page = False


# Project details
project_name = 'f90nml'
project_version = __import__(project_name).__version__
project_readme_fname = 'README.rst'
project_scripts = [os.path.join('bin', f) for f in os.listdir('bin')]

# Generate the man page if present
data_files = []
cmd_class = {}
if has_sphinx and install_man_page:
    # Create manpage build rule
    class ProjectBuildMan(BuildDoc):
        def initialize_options(self):
            BuildDoc.initialize_options(self)
            self.builder = 'man'

    # Include build_man into the main builds
    class ProjectBuild(build):
        def run(self):
            self.run_command('build_man')
            build.run(self)

    class ProjectBuildPy(build_py):
        def run(self):
            self.run_command('build_man')
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

    # NOTE: It's not a great idea to be moving files to explicit paths, so we
    # are very conservative here and only include the manpage if the manpath
    # already exists
    if os.path.isdir(os.path.join(sys.prefix, man_root, 'man')):
        data_files.append((os.path.join(man_root, 'man', 'man1'),
                            ['build/sphinx/man/{0}.1'.format(project_name)]))


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
