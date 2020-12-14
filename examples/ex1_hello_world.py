import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from occam.solid import Solid
from occam.viewer import Viewer

box = Solid.box(10, 10, 10)
v = Viewer()
v.display(box)
v.fit()
v.show()
