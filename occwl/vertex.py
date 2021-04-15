from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pnt2d
from OCC.Core.TopoDS import TopoDS_Vertex
from OCC.Core.BRep import BRep_Tool


class Vertex:
    def __init__(self, topods_vertex):
        assert isinstance(topods_vertex, TopoDS_Vertex)
        self._vertex = topods_vertex
    
    def hash(self):
        return hash(self.topods_vertex())

    def point(self):
        pt = BRep_Tool.Pnt(self.topods_vertex())
        return (pt.X(), pt.Y(), pt.Z())

    def topods_vertex(self):
        return self._vertex
