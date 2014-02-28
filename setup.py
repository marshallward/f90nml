from distutils.core import setup

with open('README.rst') as f:
    readme_rst = f.read()

setup(
    name = 'f90nml',
    version = '0.1',
    author = 'Marshall Ward',
    author_email = 'python@marshallward.org',
    description = 'Fortran 90 namelist parser',
    long_description = readme_rst,
    url = 'http://github.com/marshallward/f90nml',
    py_modules = ['f90nml'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Utilities',
    ]
)
