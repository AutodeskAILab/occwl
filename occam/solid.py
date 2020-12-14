from typing import Any, Iterable, Iterator, List, Optional, Tuple

from OCC.Core.TopoDS import (topods, TopoDS_Wire, TopoDS_Vertex, TopoDS_Edge,
                             TopoDS_Face, TopoDS_Shell, TopoDS_Solid, TopoDS_Shape,
                             TopoDS_Compound, TopoDS_CompSolid, topods_Edge,
                             topods_Vertex, TopoDS_Iterator)
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pnt2d
from OCC.Extend import TopologyUtils


class Solid:
    def __init__(self, shape):
        assert isinstance(shape, TopoDS_Solid)
        self._solid = shape
        self.top_exp = TopologyUtils.TopologyExplorer(self._solid, True)
        self._face_attr = {}

    @staticmethod
    def box(width, height, depth):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
        return Solid(BRepPrimAPI_MakeBox(width, height, depth).Shape())

    def topods_solid(self):
        return self._solid

    def get_face_color(self, face):
        return self._face_attr.get("color").get(face)

    def set_face_color(self, face, color):
        self._face_attr["color"][face] = color
        
    def vertices(self) -> Iterator[TopoDS_Vertex]:
        return self.top_exp.vertices()

    def edges(self) -> Iterator[TopoDS_Edge]:
        return self.top_exp.edges()

    def faces(self) -> Iterator[TopoDS_Face]:
        return self.top_exp.faces()
    
    def num_faces(self):
        return self.top_exp.number_of_faces()
    
    def num_edges(self):
        return self.top_exp.number_of_edges()

    def num_vertices(self):
        return self.top_exp.number_of_vertices()

    def mass(self):
        pass

    def center_of_mass(self):
        pass
