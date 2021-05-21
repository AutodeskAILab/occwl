# OCC Wrapper Library

OCCWL is a simple, lightweight Pythonic wrapper around pythonocc (python bindings for OpenCascade).


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
    conda install --user-local occwl
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

However, in Linux platform, pyqt requires an additional system dependency, `libgl1-mesa-glx`, which needs to be installed as follows:
```
sudo apt update
sudo apt install libgl1-mesa-glx
```



## Installation

- Clone OCCWL into a local directory
- CD into the cloned repository: `cd /path/to/occwl`
- Run `pip install .`


Dependencies:

- [pythonocc-core](https://github.com/tpaviot/pythonocc-core)
- One of PyQt5, PyQt4, PySide, or WxWidgets for the viewer


## Hello world

```python
from occwl.solid import Solid
from occwl.viewer import Viewer

box = Solid.make_box(10, 10, 10)
v = Viewer()
v.display(box)
v.fit()
v.show()
```

should display a box:

![hello world viewer](examples/ex1_hello_world.png "Hello world")

More examples are available in the `examples` folder.


## Running the tests

To run the occwl tests use the following command

```
python -m unittest tests
```


## Maintainers

- Pradeep Kumar Jayaraman (pradeep.kumar.jayaraman@autodesk.com)
- Joseph Lambourne (joseph.lambourne@autodesk.com)
