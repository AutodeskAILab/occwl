# OCCam

OCCam is a simple, lightweight Pythonic wrapper around pythonocc that makes it easy to work with B-reps.

## Dependencies

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

should display a box.

More examples are available in the `examples` folder.