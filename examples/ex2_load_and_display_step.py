import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from occam.io import load_step
from occam.viewer import Viewer


solid = load_step("example.stp")[0] # Returns a list of bodies from the step file
v = Viewer()
v.display(solid)
v.fit()
v.show()