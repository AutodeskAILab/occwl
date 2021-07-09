import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from occwl.solid import Solid
from occwl.viewer import Viewer

box = Solid.make_box(10, 10, 10)
v = Viewer(backend="wx")
v.display(box)
v.fit()
v.show()
