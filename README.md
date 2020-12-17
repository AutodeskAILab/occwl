# OCCam

OCCam is a simple, lightweight Pythonic wrapper around pythonocc that makes it easy to work with B-reps.

## Installation

- Clone OCCam into a local directory: `git clone https://git.autodesk.com/jayarap/occam.git`
- CD into the cloned repository: `cd /path/to/occam`
- Run `pip install .`


Dependencies:

- [pythonocc-core](https://github.com/tpaviot/pythonocc-core)
- One of PyQt5, PyQt4, PySide, or WxWidgets for the viewer


## Hello world

```python
from occam.solid import Solid
from occam.viewer import Viewer

box = Solid.box(10, 10, 10)
v = Viewer()
v.display(box)
v.fit()
v.show()
```

should display a box:

![hello world viewer](examples/ex1_hello_world.png "Hello world")

More examples are available in the `examples` folder.


Feel free to contact me for usage information or feature requests.