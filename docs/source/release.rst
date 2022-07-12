==================
Updating a release
==================

These are primarily notes to myself, since I always forget how to do this.

Preparation
-----------

1. Verify that the code passes all tests::

      python setup.py test

   Also confirm that these tests have passed on the GitHub Actions CI.

2. Create a version commit:

   a. Update the version in ``f90nml/__init__.py``

   b. Update the ``CHANGELOG``

   c. Commit these changes, denoting the new version in the log.

3. Create a tag for this commit::

   git tag -s vX.Y.Z -m "Version X.Y.Z"


Upload to PyPI
--------------

1. Delete any old ``dist`` packages::

   rm -r dist

2. Create the distribution tarballs and wheels::

   python setup.py sdist

   python setup.py bdist_wheel --universal

3. Upload using ``twine``::

   twine upload dist/*

4. Verify on PyPi:

   https://pypi.org/project/f90nml/
