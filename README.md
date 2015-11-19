# m3cfd

CFD simulation software for Martlet 3

## Installation

This software is primarily written in Python and may be installed via the
standard ``pip`` utility:

```console
$ pip install git+https://github.com/cuspaceflight/m3cfd.git
```

For developers, `pip` can be used to create a "development" install which uses
symlink magic to allow changes in files to be reflected without re-installing:

```console
$ git clone git@github.com:cuspaceflight/m3cfd.git
$ cd m3cfd
$ pip install -e .
```

## Testing

The [tox](https://tox.readthedocs.org/) automation tool is used to automate the
process of running the test suite under both Python 2.7 and whichever version of
Python 3 is installed on the system. To run the test suite:

```console
$ tox
```

