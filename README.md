<p align="center">
<a href="https://travis-ci.org/kbsezginel/angstrom">
  <img src="https://travis-ci.org/kbsezginel/angstrom.svg?branch=master" alt="Travis CI"/>
</a>
<a href="https://ci.appveyor.com/project/kbsezginel/angstrom">
  <img src="https://ci.appveyor.com/api/projects/status/lcj1f73iet2gt5up?svg=true" alt="AppVeyor"/>
</a>
<a href="https://codecov.io/gh/kbsezginel/angstrom">
  <img src="https://codecov.io/gh/kbsezginel/angstrom/branch/master/graph/badge.svg" alt="Codecov"/>
</a>
<a href='https://angstrom.readthedocs.io/en/latest/?badge=latest'>
    <img src='https://readthedocs.org/projects/angstrom/badge/?version=latest' alt='Documentation Status' />
</a>
</p>

# Ångström
A Python package for basic molecular operations with low-dependency and easy-integration.

## About
Ångström is a Python package for geometric molecular operations, molecular visualization and trajectory analysis.
The purpose of Ångström is to be a lightweight and easily integrable package.
This way it can be easily included in various simulation packages.

## Installation
You can install Ångström by cloning this repository as follows:
```
git clone https://github.com/kbsezginel/angstrom.git
cd angstrom
python setup.py install
```

Ångström will also be available through `pip` in near future.

## Tests
Unit tests are available using [pytest](https://docs.pytest.org/en/latest/).
You can run the tests by executing `pytest` in the main repository.
There will be warnings but if you would liek to suppress warnings messages you can use `pytest --disable-pytest-warnings`.
