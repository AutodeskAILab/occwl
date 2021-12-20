import pathlib

from occwl.compound import Compound
from occwl.viewer import Viewer


# Returns a list of bodies from the step file, we only need the first one
compound = Compound.load_from_step(pathlib.Path(__file__).resolve().parent.joinpath("example.stp"))
solid = next(compound.solids())

v = Viewer(backend="wx")
v.display(solid)
v.fit()
v.show()
