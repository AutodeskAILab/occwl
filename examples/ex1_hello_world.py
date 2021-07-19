from occwl.solid import Solid
from occwl.viewer import Viewer

box = Solid.make_box(10, 10, 10)
v = Viewer(backend="wx")
v.display(box)
v.fit()
v.show()
