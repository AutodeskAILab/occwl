import numpy as np
from typing import Any, Iterable, Iterator, List, Optional, Tuple

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
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pnt2d, gp_Ax2
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add, brepbndlib_AddOptimal
from OCC.Extend import TopologyUtils
from OCC.Core.BRepGProp import (
    brepgprop_LinearProperties,
    brepgprop_SurfaceProperties,
    brepgprop_VolumeProperties,
)
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.GProp import GProp_GProps
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax1, gp_Vec, gp_Trsf
from OCC.Core.ShapeUpgrade import ShapeUpgrade_ShapeDivideClosed
from OCC.Core.ShapeUpgrade import ShapeUpgrade_ShapeDivideClosedEdges
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform

import math
from occwl.edge import Edge
from occwl.face import Face
from occwl.wire import Wire
from occwl.vertex import Vertex

import occwl.geometry.geom_utils as geom_utils
from occwl.geometry.box import Box
from occwl.shape import Shape
from deprecate import deprecated
import logging


class Solid(Shape):
    """
    A solid model
    """

    def __init__(self, shape, allow_compound=False):
        if allow_compound:
            assert (isinstance(shape, TopoDS_Solid) or 
                isinstance(shape, TopoDS_Compound) or 
                isinstance(shape, TopoDS_CompSolid))
        else:
            assert isinstance(shape, TopoDS_Solid)
        super().__init__(shape)
        self._top_exp = TopologyUtils.TopologyExplorer(self.topods_shape(), True)

    @staticmethod
    def make_box(width, height, depth):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox

        return Solid(
            BRepPrimAPI_MakeBox(float(width), float(height), float(depth)).Shape()
        )

    @staticmethod
    def make_sphere(radius, center=(0, 0, 0)):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere

        return Solid(
            BRepPrimAPI_MakeSphere(geom_utils.to_gp_pnt(center), float(radius)).Shape()
        )

    @staticmethod
    def make_spherical_wedge(radius, center=(0, 0, 0), longitudinal_angle=2 * math.pi):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere

        return Solid(
            BRepPrimAPI_MakeSphere(
                geom_utils.to_gp_pnt(center), float(radius), float(longitudinal_angle)
            ).Shape()
        )

    @staticmethod
    def make_cone(
        radius_bottom,
        radius_top,
        height,
        apex_angle=2 * math.pi,
        base_point=(0, 0, 0),
        up_dir=(0, 0, 1),
    ):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCone

        return Solid(
            BRepPrimAPI_MakeCone(
                gp_Ax2(geom_utils.to_gp_pnt(base_point), geom_utils.to_gp_dir(up_dir)),
                float(radius_bottom),
                float(radius_top),
                float(height),
                float(apex_angle),
            ).Shape()
        )

    @staticmethod
    def make_cylinder(
        radius, height, angle=2 * math.pi, base_point=(0, 0, 0), up_dir=(0, 0, 1)
    ):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder

        return Solid(
            BRepPrimAPI_MakeCylinder(
                gp_Ax2(geom_utils.to_gp_pnt(base_point), geom_utils.to_gp_dir(up_dir)),
                float(radius),
                float(height),
                float(angle),
            ).Shape()
        )

    def vertices(self):
        """
        Get an iterator to go over all vertices in the solid

        Returns:
            Iterator[occwl.vertex.Vertex]: Vertex iterator
        """
        return map(Vertex, self._top_exp.vertices())

    def edges(self):
        """
        Get an iterator to go over all edges in the solid

        Returns:
            Iterator[occwl.edge.Edge]: Edge iterator
        """
        return map(Edge, self._top_exp.edges())

    def faces(self):
        """
        Get an iterator to go over all faces in the solid

        Returns:
            Iterator[occwl.face.Face]: Face iterator
        """
        return map(Face, self._top_exp.faces())

    def wires(self) -> Iterator[TopoDS_Wire]:
        """
        Get an iterator to go over all wires in the solid

        Returns:
            Iterator[occwl.wire.Wire]: Wire iterator
        """
        return map(Wire, self._top_exp.wires())

    def edges_from_face(self, face):
        """
        Get an iterator to go over the edges in a face

        Args:
            face (occwl.face.Face): Input face

        Returns:
            Iterator[occwl.edge.Edge]: Edge iterator
        """
        assert isinstance(face, Face)
        return map(Edge, self._top_exp.edges_from_face(face.topods_shape()))

    def faces_from_edge(self, edge):
        """
        Get an iterator to go over the faces adjacent to an edge

        Args:
            edge (occwl.edge.Edge): Input edge

        Returns:
            Iterator[occwl.face.Face]: Face iterator
        """
        assert isinstance(edge, Edge)
        return map(Face, self._top_exp.faces_from_edge(edge.topods_shape()))


    def faces_from_vertex(self, vertex):
        """
        Get an iterator to go over the faces adjacent to a vertex

        Args:
            edge (occwl.vertex.Vertex): Input vertex

        Returns:
            Iterator[occwl.face.Face]: Face iterator
        """
        assert isinstance(vertex, Vertex)
        return map(Face, self._top_exp.faces_from_vertex(vertex.topods_shape()))

    def vertices_from_edge(self, edge):
        """
        Get an iterator to go over the vertices bounding an edge

        Args:
            edge (occwl.edge.Edge): Input edge

        Returns:
            Iterator[occwl.vertex.Vertex]: Vertex iterator
        """
        assert isinstance(edge, Edge)
        return map(Vertex, self._top_exp.vertices_from_edge(edge.topods_shape()))

    def wires_from_face(self, face) -> Iterator[TopoDS_Wire]:
        """
        Get an iterator to go over the wires bounding a face

        Args:
            face (occwl.face.Face): Input face

        Returns:
            Iterator[occwl.wire.Wire]: Wire iterator
        """
        assert isinstance(face, Face)
        return map(Wire, self._top_exp.wires_from_face(face.topods_shape()))

    def num_faces(self):
        """
        Number of faces in the solid

        Returns:
            int: Number of faces
        """
        return self._top_exp.number_of_faces()

    def num_wires(self):
        """
        Number of wires in the solid

        Returns:
            int: Number of wires
        """
        return self._top_exp.number_of_wires()

    def num_edges(self):
        """
        Number of edges in the solid

        Returns:
            int: Number of edges
        """
        return self._top_exp.number_of_edges()

    def num_vertices(self):
        """
        Number of vertices in the solid

        Returns:
            int: Number of vertices
        """
        return self._top_exp.number_of_vertices()

    def area(self):
        """
        Compute the area of the solid

        Returns:
            float: Area
        """
        geometry_properties = GProp_GProps()
        brepgprop_SurfaceProperties(self.topods_shape(), geometry_properties)
        return geometry_properties.Mass()
        
    def volume(self, tolerance=1e-9):
        """
        Compute the volume of the solid

        Args:
            tolerance (float, optional): Tolerance. Defaults to 1e-9.

        Returns:
            float: Volume
        """
        props = GProp_GProps()
        brepgprop_VolumeProperties(self.topods_solid(), props, tolerance)
        return props.Mass()

    def center_of_mass(self, tolerance=1e-9):
        """
        Compute the center of mass of the solid

        Args:
            tolerance (float, optional): Tolerance. Defaults to 1e-9.

        Returns:
            np.ndarray: 3D point
        """
        props = GProp_GProps()
        brepgprop_VolumeProperties(self.topods_solid(), props, tolerance)
        com = props.CentreOfMass()
        return geom_utils.gp_to_numpy(com)

    def moment_of_inertia(self, point, direction, tolerance=1e-9):
        """
        Compute the moment of inertia about an axis

        Args:
            point (np.ndarray): 3D point (origin of the axis)
            direction (np.ndarray): 3D direction of the axis
            tolerance (float, optional): Tolerance. Defaults to 1e-9.

        Returns:
            float: Moment of inertia
        """
        props = GProp_GProps()
        brepgprop_VolumeProperties(self.topods_solid(), props, tolerance)
        axis = gp_Ax1(
            geom_utils.numpy_to_gp(point), geom_utils.numpy_to_gp_dir(direction)
        )
        return props.MomentOfInertia(axis)

    def box(self):
        """
        Get a quick bounding box of the solid

        Returns:
            Box: Bounding box
        """
        b = Bnd_Box()
        brepbndlib_Add(self.topods_shape(), b)
        return geom_utils.box_to_geometry(b)

    def exact_box(self, use_shapetolerance=False):
        """
        Get a slow, but accurate box for the solid.

        Args:
            use_shapetolerance (bool, optional) Include the tolerance of edges
                                                and vertices in the box.

        Returns:
            Box: Bounding box
        """
        b = Bnd_Box()
        use_triangulation = True
        brepbndlib_AddOptimal(self.topods_shape(), b, use_triangulation, use_shapetolerance)
        return geom_utils.box_to_geometry(b)


    def triangulate_all_faces(
        self,
        triangle_face_tol=0.01,  # Tolerance between triangle and surface
        tol_relative_to_face=True,  # The tolerance value is relative to the face size
        angle_tol_rads=0.1,  # Angle between normals/tangents at triangle vertices
    ):
        """
        Triangulate all the faces in the solid. You can then get the triangles 
        from each face separately using face.get_triangles().
        If you wanted triangles for the entire solid then call
        solid.get_triangles() below.
        For more details see 
        https://old.opencascade.com/doc/occt-7.1.0/overview/html/occt_user_guides__modeling_algos.html#occt_modalg_11
        
        Args:
            triangle_face_tol (float, optional): Toelrance between triangle and surface. Defaults to 0.01.
            tol_relative_to_face (bool): Whether tolerance is relative to face size
            angle_tol_rads (float, optional): Angle tolerance in radians. Defaults to 0.1.

        Returns:
            bool: Is successful
        """
        mesh = BRepMesh_IncrementalMesh(
            self.topods_shape(),
            triangle_face_tol,
            tol_relative_to_face,
            angle_tol_rads,
            True,
        )
        mesh.Perform()
        return mesh.IsDone()

    def get_triangles(
        self,
        triangle_face_tol=0.01,  # Tolerance between triangle and surface
        tol_relative_to_face=True,  # The tolerance value is relative to the face size
        angle_tol_rads=0.1,  # Angle between normals/tangents at triangle vertices
    ):
        """
        Compute and get the tessellation of the entire solid

        Args:
            triangle_face_tol (float, optional): Toelrance between triangle and surface. Defaults to 0.01.
            tol_relative_to_face (bool): Whether tolerance is relative to face size
            angle_tol_rads (float, optional): Angle tolerance in radians. Defaults to 0.1.

        Returns:
            2D np.ndarray (float): Vertices or None if triangulation failed
            2D np.ndarray (int): Faces or None if triangulation failed
        """
        ok = self.triangulate_all_faces(
            triangle_face_tol, tol_relative_to_face, angle_tol_rads
        )
        if not ok:
            # Failed to triangulate
            return None, None
        verts = []
        tris = []
        faces = self.faces()
        last_vert_index = 0
        for face in faces:
            fverts, ftris = face.get_triangles()
            verts.extend(fverts)
            for tri in ftris:
                new_indices = [index + last_vert_index for index in tri]
                tris.append(new_indices)
            last_vert_index = len(verts)
        return np.asarray(verts, dtype=np.float32), np.asarray(tris, dtype=np.int32)

    def edge_continuity(self, edge):
        """
        Get the neighboring faces' continuity at given edge

        Args:
            edge (occwl.edge.Edge): Edge

        Returns:
            GeomAbs_Shape: enum describing the continuity order
        """
        faces = list(self.faces_from_edge(edge))
        # Handle seam edges which only have one face around them
        if len(faces) == 1:
            faces.append(faces[-1])
        return edge.continuity(faces[0], faces[1])

    def find_closest_face_slow(self, datum):
        """
        Find the closest face to the given datum point.
        The function is for testing only.  It will be slow 
        as it loops over all faces in the solid.
        A quick way to find the closest entity is to call
        Solid.find_closest_point_data(), but then you
        may get a face, edge or vertex back.
        
        Args:
            datum (np.ndarray or tuple): 3D datum point

        Returns:
            Face: The closest face in the solid
        """
        return self._find_closest_shape_in_list(self.faces(), datum)

    def find_closest_edge_slow(self, datum):
        """
        Find the closest edge to the given datum point.
        The function is for testing only.  It will be slow 
        as it loops over all edges in the solid.
        A quick way to find the closest entity is to call
        Solid.find_closest_point_data(), but then you
        may get a face, edge or vertex back.
        
        Args:
            datum (np.ndarray or tuple): 3D datum point

        Returns:
            Face: The closest face in the solid
        """
        return self._find_closest_shape_in_list(self.edges(), datum)

    def _find_closest_shape_in_list(self, shapes, datum):
        """
        In this function we search all shapes in the list 
        and return the closest one.   
        Typically you would want to find the closest entity 
        which may be a face, edge or vertex.  For this you can
        use Solid.find_closest_point_data()
        """
        closest_dist_yet = np.inf
        closest_shape = None
        for s in shapes:
            closest_point_data = s.find_closest_point_data(datum)
            if closest_point_data.distance < closest_dist_yet:
                closest_shape = s
                closest_dist_yet = closest_point_data.distance
        return closest_shape
    
    def is_closed(self):
        """
        Checks and returns if the solid is closed (has no holes)

        Returns:
            bool: If closed
        """
        # In Open Cascade, unlinked (open) edges can be identified
        # as they appear in the edges iterator when ignore_orientation=False
        # but are not present in any wire
        ordered_edges = set()
        for wire in self.wires():
            for edge in wire.ordered_edges():
                ordered_edges.add(edge.topods_shape())
        unordered_edges = set([edge.topods_shape() for edge  in self.edges()])
        missing_edges = unordered_edges - ordered_edges
        return len(missing_edges) == 0

    def scale_to_unit_box(self):
        """
        Translate and scale the solid so it fits exactly 
        into the [-1, 1]^3 box

        Returns:
            occwl.Solid: The scaled version of this solid
        """
        # Get an exact box for the solid
        box = self.exact_box()
        center = box.center()
        longest_length = box.max_box_length()

        orig = gp_Pnt(0.0, 0.0, 0.0)
        center = geom_utils.numpy_to_gp(center)
        vec_center_to_orig = gp_Vec(center, orig)
        move_to_center = gp_Trsf()
        move_to_center.SetTranslation(vec_center_to_orig)

        scale_trsf = gp_Trsf()
        scale_trsf.SetScale(orig, 2.0/longest_length)
        trsf_to_apply = scale_trsf.Multiplied(move_to_center)
        
        apply_transform = BRepBuilderAPI_Transform(trsf_to_apply)
        apply_transform.Perform(self.topods_shape())
        transformed_solid = apply_transform.ModifiedShape(self.topods_shape())

        return Solid(transformed_solid)

    def split_all_closed_faces(self, max_tol=0.01, precision=0.01, num_splits=1):
        """
        Split all the closed faces in this solid

        Args:
            max_tol (float, optional): Maximum tolerance allowed. Defaults to 0.01.
            precision (float, optional): Precision of the tool when splitting. Defaults to 0.01.
            num_splits (int, optional): Number of splits to perform. Each split face will result in num_splits + 1 faces. Defaults to 1.

        Returns:
            occwl.solid.Solid: Solid with closed faces split
        """
        divider = ShapeUpgrade_ShapeDivideClosed(self.topods_shape())
        divider.SetPrecision(precision)
        divider.SetMinTolerance(0.1 * max_tol)
        divider.SetMaxTolerance(max_tol)
        divider.SetNbSplitPoints(num_splits)
        ok = divider.Perform()
        if not ok:
            # Splitting failed or there were no closed faces to split
            # Return the original solid
            return self
        return Solid(divider.Result())

    def split_all_closed_edges(self, max_tol=0.01, precision=0.01, num_splits=1):
        """
        Split all the closed edges in this solid

        Args:
            max_tol (float, optional): Maximum tolerance allowed. Defaults to 0.01.
            precision (float, optional): Precision of the tool when splitting. Defaults to 0.01.
            num_splits (int, optional): Number of splits to perform. Each split edge will result in num_splits + 1 edges. Defaults to 1.

        Returns:
            occwl.solid.Solid: Solid with closed edges split
        """
        divider = ShapeUpgrade_ShapeDivideClosedEdges(self.topods_shape())
        divider.SetPrecision(precision)
        divider.SetMinTolerance(0.1 * max_tol)
        divider.SetMaxTolerance(max_tol)
        divider.SetNbSplitPoints(num_splits)
        ok = divider.Perform()
        if not ok:
            # Splitting failed or there were no closed edges to split
            # Return the original solid
            return self
        return Solid(divider.Result())

    def check_unique_oriented_edges(self):
        ordered_edges = set()
        for wire in self.wires():
            for oriented_edge in wire.ordered_edges():
                is_reversed = oriented_edge.reversed()
                tup = (oriented_edge, is_reversed)
               
                # We want to detect the case where the oriented
                # edges are not unique
                if tup in ordered_edges:
                    # Here we see the same oriented edges
                    # appears twice in the solid.  This is the 
                    # failure case we need to flag 
                    return False

                ordered_edges.add(tup)

        return True
