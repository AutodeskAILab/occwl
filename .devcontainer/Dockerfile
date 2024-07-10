# syntax=docker/dockerfile:1.4
FROM --platform=linux/amd64 python:3.9 as base

RUN python -m pip install --upgrade pip

FROM base as dev

# Insgtall OCC requirements
RUN apt-get update
RUN  apt-get install -y ffmpeg libsm6 libxext6

# Install conda
RUN mkdir -p ~/miniconda3 && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh && \
    bash ~/miniconda3/miniconda.sh -b -u -p /miniconda3 && \
    rm -rf ~/miniconda3/miniconda.sh && \
    /miniconda3/bin/conda init bash

ARG PROJ_DIR=/proj
ARG PIP_CACHE=/root/.cache/pip
WORKDIR ${PROJ_DIR}

# Create conda environment
COPY environment.yml .
RUN --mount=type=cache,target=/miniconda3/pkgs,id=conda \
    /miniconda3/bin/conda env create -f environment.yml
SHELL ["conda", "run", "--no-capture-output", "-n", "occwl_dev", "/bin/bash", "-c"]

# Install Python dependencies
# COPY setup.py .
# RUN mkdir -p ${PROJ_DIR}/src
# RUN --mount=type=cache,target=${PIP_CACHE},id=pip \
#     /miniconda3/bin/conda run -n occwl_dev python -m \
#     pip install -v --cache-dir ${PIP_CACHE} -e .

ENTRYPOINT [ "/bin/bash", "-c" ]