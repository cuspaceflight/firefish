#!/bin/bash
#
# Run tests on Travis CI worker. Requires that travis-install.sh has been run.

# Exit on error
set -e

# We need to add the OpenFOAM applications to the PATH. OpenFOAM comes with a
# script to do this for us.
source /opt/openfoam30/etc/bashrc

# Now switch on logging so that we don't get log spam from the OpenFOAM setup
set -x

# If the TOX_ENV environment variable is set, run tox for that testenv.
if [ ! -z "${TOX_ENV}" ]; then
    tox -e "${TOX_ENV}"
fi

