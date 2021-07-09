import os
import sys
import pathlib

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from occwl.io import load_step
from occwl.viewer import Viewer


solid = load_step(pathlib.Path(__file__).resolve().parent.joinpath("example.stp"))[
    0
]  # Returns a list of bodies from the step file
v = Viewer(backend="wx")
v.display(solid)
v.fit()
v.show()
