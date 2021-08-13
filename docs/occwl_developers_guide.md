# OCCWL developers and maintainers guide

## Installing locally

- Clone OCCWL into a local directory
- CD into the cloned repository: `cd /path/to/occwl`
- Create an environment

```
conda env create -f environment.yml
conda activate occwl_dev
```
Then you can either use setuptools to install occwl locally
```
pip install .
```
or you can add the full path to the `src/occwl` folder to the `PYTHONPATH` environment variable:

- Linux:
```
 export PYTHONPATH=$PYTHONPATH:/path/to/occwl/src/
```
- Windows:
```
set PYTHONPATH=%PYTHONPATH%;path\to\occwl\src\occwl
```

To check everything is working run 
```
python -m unittest
```

## Running the tests

To run the occwl tests use the following command

```
python -m unittest tests
```



## Build Conda Package from Source and Upload to Anaconda

- Build and test package locally:
    
    1. Set the package version by modifying version parameters in `ci/conda/meta.yaml` and `setup.py` files.

    2. Build and test package:
    ```
    sh build_conda_package.sh
    ```

- Upload the new local package to Anaconda:
    
    1. Create an Anaconda account at [https://anaconda.org/](https://anaconda.org/)
    
    2. Login to Anaconda:
        ```
        anaconda login 
        ```

    3. Upload package to Anaconda channel:
        ```
        anaconda upload /Users/<user_name>/miniconda/conda-bld/noarch/occwl-<version>-py_0.tar.bz2
        ```

- Build and test package and upload to Anaconda:

    1. Create an Anaconda account at [https://anaconda.org/](https://anaconda.org/)

    2. Set the package version by modifying version parameters in `ci/conda/meta.yaml` and `setup.py`

    3. Build and test package and upload to Anaconda:
    ```
    sh build_conda_package.sh <anaconda_username> 
    ```

## Install Conda Package
- Install conda package from local channel
    ```
    conda install --use-local occwl
    ```
    or
    ```
    conda install -c file:///Users/<user_name>/miniconda/envs/<env_name>/conda-bld/ occwl
    ```

- Install conda Package from Anaconda

    ```
    conda install -c <anaconda_username> -c conda-forge occwl
    ```
    Note that packages in Anaconda account are public by default and can be installed
    by other usesr without login to Anaconda.

Note the following dependencies will also be automatically installed:
 - [pythonocc-core](https://github.com/tpaviot/pythonocc-core)
 - pyqt
 - pyside2
 - wxpython
 - numpy
 - networkx
 - pyDeprecate

However, in Linux platform, pyqt requires an additional system dependency, `libgl1-mesa-glx`, which needs to be installed as follows:
```
sudo apt update
sudo apt install libgl1-mesa-glx
```




