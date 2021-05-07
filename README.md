# OCC Wrapper Library

OCCWL is a simple, lightweight Pythonic wrapper around pythonocc (python bindings for OpenCascade).

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
