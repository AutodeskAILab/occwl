from typing import Any, Iterable, Iterator, List, Optional, Tuple

from OCC.Core.TopoDS import (topods, TopoDS_Wire, TopoDS_Vertex, TopoDS_Edge,
                             TopoDS_Face, TopoDS_Shell, TopoDS_Solid, TopoDS_Shape,
                             TopoDS_Compound, TopoDS_CompSolid, topods_Edge,
                             topods_Vertex, TopoDS_Iterator)
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pnt2d, gp_Ax2
from OCC.Extend import TopologyUtils
from OCC.Core.BRepGProp import (brepgprop_LinearProperties,
                                brepgprop_SurfaceProperties,
                                brepgprop_VolumeProperties)
from OCC.Core.GProp import GProp_GProps
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax1
import math
from occam.edge import Edge
from occam.face import Face
from occam.vertex import Vertex


class Solid:
    def __init__(self, shape):
        assert isinstance(shape, TopoDS_Solid)
        self._solid = shape
        self._top_exp = TopologyUtils.TopologyExplorer(self._solid, True)

    @staticmethod
    def box(width, height, depth):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
        return Solid(BRepPrimAPI_MakeBox(width, height, depth).Shape())

    @staticmethod
    def sphere(radius, center=(0, 0, 0)):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere
        return Solid(BRepPrimAPI_MakeSphere(gp_Pnt(*center), radius).Shape())
    
    @staticmethod
    def spherical_wedge(radius, center=(0, 0, 0), longitudinal_angle=2*math.pi):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere
        return Solid(BRepPrimAPI_MakeSphere(gp_Pnt(*center), radius, longitudinal_angle).Shape())
    
    @staticmethod
    def cone(radius_bottom, radius_top, height, apex_angle=2*math.pi, base_point=(0, 0, 0), up_dir=(0, 0, 1)):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCone
        return Solid(BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(*base_point), gp_Dir(*up_dir)), radius_bottom, radius_top, height, apex_angle).Shape())
    
    @staticmethod
    def cylinder(radius, height, angle=2*math.pi, base_point=(0, 0, 0), up_dir=(0, 0, 1)):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
        return Solid(BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(*base_point), gp_Dir(*up_dir)), radius, height, angle).Shape())

    def topods_solid(self):
        return self._solid

    def vertices(self) -> Iterator[TopoDS_Vertex]:
        return map(Vertex, self._top_exp.vertices())

    def edges(self) -> Iterator[TopoDS_Edge]:
        return map(Edge, self._top_exp.edges())

    def faces(self) -> Iterator[TopoDS_Face]:
        return map(Face, self._top_exp.faces())
    
    def edges_from_face(self, face):
        assert isinstance(face, Face)
        return map(Edge, self._top_exp.edges_from_face(face.topods_face()))
    
    def faces_from_edge(self, edge):
        assert isinstance(edge, Edge)
        return map(Face, self._top_exp.faces_from_edge(edge.topods_edge()))

    def num_faces(self):
        return self._top_exp.number_of_faces()
    
    def num_edges(self):
        return self._top_exp.number_of_edges()

    def num_vertices(self):
        return self._top_exp.number_of_vertices()

    def volume(self, tolerance=1e-9):
        props = GProp_GProps()
        brepgprop_VolumeProperties(self.topods_solid(), props, tolerance)
        return props.Mass()

    def center_of_mass(self, tolerance=1e-9):
        props = GProp_GProps()
        brepgprop_VolumeProperties(self.topods_solid(), props, tolerance)
        com = props.CentreOfMass()
        return (com.X(), com.Y(), com.Z())

    def moment_of_inertia(self, point, direction, tolerance=1e-9):
        props = GProp_GProps()
        brepgprop_VolumeProperties(self.topods_solid(), props, tolerance)
        return props.MomentOfInertia(gp_Ax1(gp_Pnt(*point), gp_Dir(*direction)))