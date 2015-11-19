#!/bin/bash
#
# Run tests on Travis CI worker. Requires that travis-install.sh has been run.

# Log commands and exit on error
set -xe

# If the TOX_ENV environment variable is set, run tox for that testenv.
if [ ! -z "${TOX_ENV}" ]; then
    tox -e "${TOX_ENV}"
fi

