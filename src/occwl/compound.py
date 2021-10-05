from occwl.solid import Solid


class Compound(Solid):
    """
    A compound which can be worked with as many solids
    lumped together.
    """
    def __init__(self, shape):
        assert isinstance(shape, TopoDS_Compound) or isinstance(shape, TopoDS_CompSolid)
        super().__init__(shape, allow_compound=True)
        
    def solids(self):
        return map(Face, self._top_exp.solids())