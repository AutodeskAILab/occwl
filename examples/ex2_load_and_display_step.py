import pathlib

from occwl.io import load_step
from occwl.viewer import Viewer


# Returns a list of bodies from the step file, we only need the first one
solid = load_step(pathlib.Path(__file__).resolve().parent.joinpath("example.stp"))[0]

v = Viewer(backend="wx")
v.display(solid)
v.fit()
v.show()
