from OCC.Core.TopoDS import (
    topods,
    TopoDS_Wire,
    TopoDS_Vertex,
    TopoDS_Edge,
    TopoDS_Face,
    TopoDS_Shell,
    TopoDS_Solid,
    TopoDS_Shape,
    TopoDS_Compound,
    TopoDS_CompSolid,
    topods_Edge,
    topods_Vertex,
    TopoDS_Iterator,
)

from occwl.solid import Solid


class Compound(Solid):
    """
    A compound which can be worked with as many solids
    lumped together.
    """
    def __init__(self, shape):
        assert (isinstance(shape, TopoDS_Solid) or 
                isinstance(shape, TopoDS_Compound) or 
                isinstance(shape, TopoDS_CompSolid))
        super().__init__(shape, allow_compound=True)
        
    def solids(self):
        return map(Solid, self._top_exp.solids())