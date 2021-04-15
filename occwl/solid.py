from typing import Any, Iterable, Iterator, List, Optional, Tuple

from OCC.Core.TopoDS import (topods, TopoDS_Wire, TopoDS_Vertex, TopoDS_Edge,
                             TopoDS_Face, TopoDS_Shell, TopoDS_Solid, TopoDS_Shape,
                             TopoDS_Compound, TopoDS_CompSolid, topods_Edge,
                             topods_Vertex, TopoDS_Iterator)
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pnt2d, gp_Ax2
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Extend import TopologyUtils
from OCC.Core.BRepGProp import (brepgprop_LinearProperties,
                                brepgprop_SurfaceProperties,
                                brepgprop_VolumeProperties)
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.GProp import GProp_GProps
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax1

import math
from occwl.edge import Edge
from occwl.face import Face
from occwl.vertex import Vertex

import geometry.geom_utils as geom_utils
from geometry.box import Box


class Solid:
    def __init__(self, shape):
        assert isinstance(shape, TopoDS_Solid)
        self._solid = shape
        self._top_exp = TopologyUtils.TopologyExplorer(self._solid, True)

    @staticmethod
    def make_box(width, height, depth):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
        return Solid(BRepPrimAPI_MakeBox(width, height, depth).Shape())

    @staticmethod
    def make_sphere(radius, center=(0, 0, 0)):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere
        return Solid(BRepPrimAPI_MakeSphere(gp_Pnt(*center), radius).Shape())
    
    @staticmethod
    def make_spherical_wedge(radius, center=(0, 0, 0), longitudinal_angle=2*math.pi):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere
        return Solid(BRepPrimAPI_MakeSphere(gp_Pnt(*center), radius, longitudinal_angle).Shape())
    
    @staticmethod
    def make_cone(radius_bottom, radius_top, height, apex_angle=2*math.pi, base_point=(0, 0, 0), up_dir=(0, 0, 1)):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCone
        return Solid(BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(*base_point), gp_Dir(*up_dir)), radius_bottom, radius_top, height, apex_angle).Shape())
    
    @staticmethod
    def make_cylinder(radius, height, angle=2*math.pi, base_point=(0, 0, 0), up_dir=(0, 0, 1)):
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
    
    def vertices_from_edge(self, edge):
        assert isinstance(edge, Edge)
        return map(Vertex, self._top_exp.vertices_from_edge(edge.topods_edge()))

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
        return geom_utils.gp_to_numpy(com)

    def moment_of_inertia(self, point, direction, tolerance=1e-9):
        props = GProp_GProps()
        brepgprop_VolumeProperties(self.topods_solid(), props, tolerance)
        axis = gp_Ax1(
            geom_utils.numpy_to_gp(point), 
            geom_utils.numpy_to_gp_dir(direction)
        )
        return props.MomentOfInertia(axis)

    def box(self):
        b = Bnd_Box()
        brepbndlib_Add(self._solid, b)
        max_corner = b.CornerMax()
        min_corner = b.CornerMin()

        bb = Box(geom_utils.gp_to_numpy(min_corner))
        bb.encompass_point(geom_utils.gp_to_numpy(max_corner))
        return bb
        
    def triangulate_all_faces(
        self, 
        triangle_face_tol = 0.01,     # Tolerance between triangle and surface
        tol_relative_to_face = True,  # The tolerance value is relative to the face size
        angle_tol_rads = 0.1          # Angle between normals/tangents at triangle vertices
        ):
        """
        Triangulate all the faces.   You can then get the triangles 
        from each face separately using face.get_triangles().
        If you wanted triangles for the entire solid then call
        solid.get_triangles() below.
        For more details see 
        https://old.opencascade.com/doc/occt-7.1.0/overview/html/occt_user_guides__modeling_algos.html#occt_modalg_11
        
        Returns True is successful
        """
        mesh = BRepMesh_IncrementalMesh(
            self._solid, 
            triangle_face_tol, 
            tol_relative_to_face, 
            angle_tol_rads, 
            True
        )
        mesh.Perform()
        return mesh.IsDone()
	


    def get_triangles(
        self,
        triangle_face_tol = 0.01,     # Tolerance between triangle and surface
        tol_relative_to_face = True,  # The tolerance value is relative to the face size
        angle_tol_rads = 0.1          # Angle between normals/tangents at triangle vertices
        ):
        ok  = self.triangulate_all_faces(triangle_face_tol, tol_relative_to_face, angle_tol_rads)
        verts = []
        tris = []
        if not ok:
            # Failed to triangulate
            return verts, tris
        faces = self.faces()
        last_vert_index = 0
        for face in faces:
            fverts, ftris = face.get_triangles()
            verts.extend(fverts)
            for tri in ftris:
                new_indices = [index+last_vert_index for index in tri]
                tris.append(new_indices)
            last_vert_index = len(verts)
        return verts, tris

    def edge_continuity(self, edge):
        faces = list(self.faces_from_edge(edge))
        # Handle seam edges which only have one face around them
        if len(faces) == 1:
           faces.append(faces[-1])
        return edge.continuity(faces[0], faces[1])
