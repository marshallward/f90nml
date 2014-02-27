#!/usr/bin/env python

from distutils.core import setup

with open('README.txt') as f:
    readme_txt = f.read()

setup(
    name = 'f90nml',
    version = '0.1',
    author = 'Marshall Ward',
    author_email = 'python@marshallward.org',
    description = 'Fortran 90 namelist parser',
    long_description = readme_txt,
    license = 'PSFL',
    keywords = 'fortran f90 namelist parser',
    url = 'http://github.com/marshallward/f90nml',
    py_modules = ['f90nml'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Python Software Foundation License',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ]
)
