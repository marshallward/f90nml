==========================
Contributing to ``f90nml``
==========================

``f90nml`` development is driven by user feedback, and your contributions help
to find bugs, add features, and improve performance.  This is a small guide to
help those who wish to contribute.


Development Portal
==================

Code development is currently hosted at GitHub.  Issues, feature requests, and
code contributions are currently handled there.

   https://github.com/marshallward/f90nml


Reporting errors
================

Any errors or general problems can be reported on GitHub's Issue tracker:

   https://github.com/marshallward/f90nml/issues

The quickest way resolve a problem is to go through the following steps:

* Have I tested this on the latest GitHub (``master``) version?

* Have I provided a sample code block which reproduces the error?  Have I
  tested the code block?

* Have I included the necessary input or output files?

  Sometimes a file attachment is required, since uncommon whitespace or
  Unicode characters may be missing from a standard cut-and-paste of the file.

* Have I provided a backtrace from the error?

Usually this is enough information to reproduce and resolve the problem.  In
some cases, we may need more information about your system, including the
following:

* Your ``f90nml`` version::

     >>> import f90nml
     >>> f90nml.__version__
     '1.1'

* The version and build of python::

     >>> import sys
     >>> print(sys.version)
     3.6.8 (default, Apr 25 2019, 21:02:35)
     [GCC 4.8.5 20150623 (Red Hat 4.8.5-36)]

* Your operating system (Linux, OS X, Windows, etc.), and your distribution if
  relevant.

While more information can help, the most important step is to report the
problem, and any missing information can be provided over the course of the
discussion.


Feature requests
================

Feature requests are welcome, and can be submitted as Issues in the GitHub
tracker.

   https://github.com/marshallward/f90nml/issues

When preparing a feature request, consider providing the following information:

* What problem is this feature trying to solve?

* Is it solvable using Python intrinsics?  How is it currently handled in
  similar modules?

* Does the feature current exist in similar modules (`JSON`_, `YAML`_, etc.)?

* Can you provide an example code block demonstrating the feature?

* For ``Namelist`` changes, is it compatible with the ``dict`` parent class?

* Does this feature require any new dependencies (e.g. NumPy)?

As a self-supported project, time is often limited and feature requests are
often a lower priority than bug fixes or ongoing work, but a strong case can
help to prioritize feature development.

.. _JSON: https://docs.python.org/3/library/json.html
.. _YAML: https://pyyaml.org/

Contributing to f90nml
======================

Fixes and features are very welcome to ``f90nml``, and are greatly encouraged.
Much of the functionality of the ``Parser`` and ``Namelist`` classes have been
either requested or contributed by other users.

If you are concerned that a project may not be suitable or may conflict with
ongoing work, then feel free to submit a feature request with comment noting
that you are happy to provide the feature.

Feature should be sent as pull requests via GitHub, specifically to the
``master`` branch, which acts as the main development branch.

Explicit patches via email are also welcome, although they are a bit more work
to process.

When preparing a pull request, consider the following advice:

* Commit logs should be long-form.  Don't use ``commit -m "Added a feature!"``;
  instead provide a multiline description of your changes.

  Single line commits are acceptable for very minor changes, such as
  whitespace.

* Commit messages should generally try to be standalone and ought to avoid
  references to explicit GitHub content, such as issue numbers or usernames.

* Code changes must pass existing tests::

     $ python setup.py test

* Code changes ought to satisfy PEP8, including line length limit.  The
  following should raise no warnings::

     $ pycodestyle f90nml

  ``pycodestyle`` is available on PyPI via pip::

     $ pip install pycodestyle

* Providing a test case for your example would be greatly appreciated.  See
  ``tests/test_f90nml.py`` for examples.

* Features should generally only depend on the standard library.  Any features
  requiring an external dependency should only be enabled when the dependency
  is available.

In practice, contributions are rare and it's not difficult to sort out these
issues inside of the pull request.


Have Fun
========

Most importantly, remember that it is more important to contribute than to
follow the rules and never contribute.  Issues can be sorted out in real time,
and everything can be amended in the world of software.
