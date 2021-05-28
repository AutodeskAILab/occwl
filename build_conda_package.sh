#!/bin/sh

# This script builds a conda package and uploads 
# package to an anaconda channel if anaconda username
# is provided as an input argument to the script.
# Note conda package will only be uploaded to
# anaconda channel if all package tests succeed.

# install required packages
conda install conda-build -y
conda update conda -y
conda update conda-build -y
conda install anaconda-client -y

# login to anaconda if anaconda username is provided
if [ "$1" ]; then
    conda config --set anaconda_upload yes
    anaconda login --username "$1"
else
    conda config --set anaconda_upload no
fi

# install libgl1-mesa-glx in Linux. refre to 
# https://github.com/conda-forge/pygridgen-feedstock/issues/10 for more information
unamestr=$(uname)
if [ "$unamestr" = 'Linux' ]; then
    if command -v sudo; then
        sudo apt update -y
        sudo apt install libgl1-mesa-glx -y
    else
        apt update -y
        apt install libgl1-mesa-glx -y
    fi
fi

# build conda package
conda build . -c conda-forge

# conda install --use-local occwl