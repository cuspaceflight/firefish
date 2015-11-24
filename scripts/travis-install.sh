#!/bin/bash
#
# Install software within the Travis CI environment. Requires an Ubuntu Trusty
# worker and sudo access. This script can be viewed additionally as tested
# installation instructions(!)
#
# DO NOT RUN THIS SCRIPT DIRECTLY WITH ROOT PRIVILEGES.

# Log commands and exit on error
set -xe

# Refresh the apt package cache and install the apt repository management
# tooling.
sudo apt-get -y update
sudo apt-get -y install software-properties-common

# Add OpenFOAM Ubuntu package repository
sudo add-apt-repository -y http://www.openfoam.org/download/ubuntu

# Refresh apt cache from new repositories
sudo apt-get -y update

# Install openfoam. Annoyingly openfoam do not appear to sign their packages so
# we have to trust that $BAD_GUYS are not in the middle of our connection. Apt
# will only install unsigned packages with --force-yes.
sudo apt-get -y --force-yes install openfoam30

# Install tox to run our test suite
pip install tox

