Sedate
======

.. image:: https://img.shields.io/pypi/v/sedate.svg
    :target: https://pypi.org/project/sedate
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/sedate.svg
    :target: https://pypi.org/project/sedate
    :alt: Python versions

.. image:: https://github.com/seantis/sedate/actions/workflows/python-tox.yaml/badge.svg
    :target: https://github.com/seantis/sedate/actions
    :alt: Tests

.. image:: https://codecov.io/gh/seantis/sedate/branch/master/graph/badge.svg?token=gMGL85OASa
    :target: https://codecov.io/gh/seantis/sedate
    :alt: Codecov.io

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

Date/time helper functions used by various Seantis packages.

There are projects like `Arrow <https://github.com/crsmithdev/arrow>`_ or
`Delorean <https://github.com/crsmithdev/arrow>`_ which provide ways to work
with timezones without having to think about it too much.

Seantis doesn't use them because we *want* to reason about these things,
to ensure they are correct, and partly because of self-loathing.

Adding another layer makes this reasoning harder.

Run the Tests
-------------

Install tox and run it::

    pip install tox
    tox

Limit the tests to a specific python version::

    tox -e py37

Conventions
-----------

Sedate follows PEP8 as close as possible. To test for it run::

    tox -e lint

Sedate uses `Semantic Versioning <http://semver.org/>`_


Development
-----------

Setup your local development environment::

    python3.8 -m venv venv
    source venv/bin/activate
    pip install .[dev]
    pre-commit install

License
-------
sedate is released under GPLv2
