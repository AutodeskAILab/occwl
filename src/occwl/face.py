import logging

import numpy as np
from deprecate import deprecated
from OCC.Core.BRep import BRep_Tool, BRep_Tool_Surface
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.BRepFill import BRepFill_Filling
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCC.Core.BRepTools import breptools_UVBounds
from OCC.Core.BRepTopAdaptor import BRepTopAdaptor_FClass2d
from OCC.Core.GeomAbs import (GeomAbs_BezierSurface, GeomAbs_BSplineSurface,
                              GeomAbs_C0, GeomAbs_C1, GeomAbs_C2, GeomAbs_C3,
                              GeomAbs_Cone, GeomAbs_Cylinder, GeomAbs_G1,
                              GeomAbs_G2, GeomAbs_OffsetSurface,
                              GeomAbs_OtherSurface, GeomAbs_Plane,
                              GeomAbs_Sphere, GeomAbs_SurfaceOfExtrusion,
                              GeomAbs_SurfaceOfRevolution, GeomAbs_Torus)
from OCC.Core.GeomLProp import GeomLProp_SLProps
from OCC.Core.gp import gp_Dir, gp_Pnt, gp_Pnt2d, gp_TrsfForm
from OCC.Core.ShapeAnalysis import ShapeAnalysis_Surface
from OCC.Core.TopAbs import TopAbs_IN, TopAbs_REVERSED
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TopoDS import TopoDS_Face

from occwl.base import BoundingBoxMixin, TriangulatorMixin, WireContainerMixin, \
    EdgeContainerMixin, VertexContainerMixin, SurfacePropertiesMixin
from occwl.edge import Edge
from occwl.shape import Shape

import occwl.geometry.geom_utils as geom_utils
import occwl.geometry.interval as Interval
from occwl.geometry.box import Box


class Face(Shape, BoundingBoxMixin, TriangulatorMixin, WireContainerMixin, \
    EdgeContainerMixin, VertexContainerMixin, SurfacePropertiesMixin):
    """
    A topological face in a solid model
    Represents a 3D surface bounded by a Wire
    """

    def __init__(self, topods_face):
        assert isinstance(topods_face, TopoDS_Face)
        super().__init__(topods_face)
        self._trimmed = BRepTopAdaptor_FClass2d(self.topods_shape(), 1e-9)

    @staticmethod
    def make_prism(profile_edge, vector, return_first_last_shapes=False):
        """
        Make a face from a profile edge by sweeping/extrusion

        Args:
            profile_edge (occwl.edge.Edge): Edge
            vector (np.ndarray): Direction and length of extrusion
            return_first_last_shapes (bool, optional): Whether to return the base and top shapes of the result. Defaults to False.

        Returns:
            occwl.Face: Face created by sweeping the edge
            or None: if error
            occwl.Edge, occwl.Edge (optional): Returns the base and top edges of return_first_last_shapes is True.
        """
        assert isinstance(profile_edge, Edge)
        gp_vector = geom_utils.numpy_to_gp_vec(vector)
        prism = BRepPrimAPI_MakePrism(profile_edge.topods_shape(), gp_vector)
        if not prism.IsDone():
            return None
        if return_first_last_shapes:
            return (
                Face(prism.Shape()),
                Edge(prism.FirstShape()),
                Edge(prism.LastShape()),
            )
        return Face(prism.Shape())

    @staticmethod
    def make_nsided(edges, continuity="C0", points=None):
        """
        Make an n-sided fill-in face with the given edges, their continuities, and optionally a
        set of punctual points

        Args:
            edges (List[occwl.edge.Edge]): A list of edges for creating the fill-in face
            continuity (str or List[str]): A single string or a list of strings, one for each given edge.
                                           Must be one of "C0", "C1", "G1", "C2", "G2", "C3"
            points (np.ndarray, optional): Set of points to constrain the fill-in surface. Defaults to None.

        Returns:
            occwl.face.Face: Filled-in face
        """
        fill = BRepFill_Filling()

        # A helper function to convert strings to Geom_Abs_ enums
        def str_to_continuity(string):
            if string == "C0":
                return GeomAbs_C0
            elif string == "C1":
                return GeomAbs_C1
            elif string == "G1":
                return GeomAbs_G1
            elif string == "C2":
                return GeomAbs_C2
            elif string == "G2":
                return GeomAbs_G2
            elif string == "C3":
                return GeomAbs_C3

        if isinstance(continuity, str):
            assert continuity in ("C0", "C1", "C2")
            occ_continuity = str_to_continuity(continuity)
            for edg in edges:
                fill.Add(edg.topods_shape(), occ_continuity)
        elif isinstance(continuity, list):
            assert len(edges) == len(continuity), "Continuity should be provided for each edge"
            for edg, cont in zip(edges, continuity):
                occ_cont = str_to_continuity(cont)
                fill.Add(edg.topods_shape(), occ_cont)

        # Add points to contrain shape if provided
        if points:
            for pt in points:
                fill.Add(geom_utils.to_gp_pnt(pt))
        fill.Build()
        face = fill.Face()
        return Face(face)

    @staticmethod
    def make_from_wires(wires):
        """
        Make a face from PLANAR wires

        Args:
            wires (List[occwl.wire.Wire]): List of wires

        Returns:
            occwl.face.Face or None: Returns a Face or None if the operation failed
        """
        face_builder = BRepBuilderAPI_MakeFace()
        for wire in wires:
            face_builder.Add(wire.topods_shape())
        face_builder.Build()
        if not face_builder.IsDone():
            return None
        return Face(face_builder.Face())

    def inside(self, uv):
        """
        Check if the uv-coordinate is inside the visible region of the face (excludes points that lie on the boundary)

        Args:
            uv (np.ndarray or tuple): Surface parameter
        
        Returns:
            bool: Is inside
        """
        result = self._trimmed.Perform(gp_Pnt2d(uv[0], uv[1]))
        return result == TopAbs_IN
    
    def visibility_status(self, uv):
        """
        Check if the uv-coordinate in on the visible region of the face

        Args:
            uv (np.ndarray or tuple): Surface parameter
        
        Returns:
            int (TopAbs_STATE enum): 0: TopAbs_IN, 1: TopAbs_OUT, 2: TopAbs_ON, 3: TopAbs_UNKNOWN
        """
        result = self._trimmed.Perform(gp_Pnt2d(uv[0], uv[1]))
        return int(result)

    def surface(self):
        """
        Get the face surface geometry

        Returns:
            OCC.Geom.Handle_Geom_Surface: Interface to all surface geometry
        """
        loc = TopLoc_Location()
        surf = BRep_Tool_Surface(self.topods_shape(), loc)
        if not loc.IsIdentity():
            tsf = loc.Transformation()
            np_tsf = geom_utils.to_numpy(tsf)
            assert np.allclose(np_tsf, np.eye(4)), \
                "Requesting surface for transformed face. /n\
                Call solid.set_transform_to_identity() to remove the transform \
                or compound.Transform(np.eye(4)) to bake in the assembly transform"
        return surf

    def reversed_face(self):
        """
        Return a copy of this face with the orientation reversed.
        
        Returns:
            occwl.face.Face: A face with the opposite orientation to this face.
        """
        return Face(self.topods_shape().Reversed())

    def specific_surface(self):
        """
        Get the specific face surface geometry

        Returns:
            OCC.Geom.Handle_Geom_*: Specific geometry type for the surface geometry
        """
        if not self.topods_shape().Location().IsIdentity():
            tsf = self.topods_shape().Location().Transformation()
            np_tsf = geom_utils.to_numpy(tsf)
            assert np.allclose(np_tsf, np.eye(4)), \
                "Requesting surface for transformed face. /n\
                Call solid.set_transform_to_identity() to remove the transform /n\
                or compound.transform(np.eye(4)) to bake in the assembly transform"
        srf = BRepAdaptor_Surface(self.topods_shape())
        surf_type = self.surface_type()
        if surf_type == "plane":
            return srf.Plane()
        if surf_type == "cylinder":
            return srf.Cylinder()
        if surf_type == "cone":
            return srf.Cone()
        if surf_type == "sphere":
            return srf.Sphere()
        if surf_type == "torus":
            return srf.Torus()
        if surf_type == "bezier":
            return srf.Bezier()
        if surf_type == "bspline":
            return srf.BSpline()
        raise ValueError("Unknown surface type: ", surf_type)


    def point(self, uv):
        """
        Evaluate the face geometry at given parameter

        Args:
            uv (np.ndarray or tuple): Surface parameter
        
        Returns:
            np.ndarray: 3D Point
        """
        loc = TopLoc_Location()
        surf = BRep_Tool_Surface(self.topods_shape(), loc)
        pt = surf.Value(uv[0], uv[1])
        pt = pt.Transformed(loc.Transformation())
        return geom_utils.gp_to_numpy(pt)

    def tangent(self, uv):
        """
        Compute the tangents of the surface geometry at given parameter

        Args:
            uv (np.ndarray or tuple): Surface parameter

        Returns:
            Pair of np.ndarray or None: 3D unit vectors
        """
        loc = TopLoc_Location()
        surf = BRep_Tool_Surface(self.topods_shape(), loc)
        dU, dV = gp_Dir(), gp_Dir()
        res = GeomLProp_SLProps(surf, uv[0], uv[1], 1, 1e-9)
        if res.IsTangentUDefined() and res.IsTangentVDefined():
            res.TangentU(dU), res.TangentV(dV)
            dU.Transformed(loc.Transformation())
            dV.Transformed(loc.Transformation())
            return (geom_utils.gp_to_numpy(dU)), (geom_utils.gp_to_numpy(dV))
        return None, None

    def normal(self, uv):
        """
        Compute the normal of the surface geometry at given parameter

        Args:
            uv (np.ndarray or tuple): Surface parameter

        Returns:
            np.ndarray: 3D unit normal vector
        """
        loc = TopLoc_Location()
        surf = BRep_Tool_Surface(self.topods_shape(), loc)
        res = GeomLProp_SLProps(surf, uv[0], uv[1], 1, 1e-9)
        if not res.IsNormalDefined():
            return (0, 0, 0)
        gp_normal = res.Normal()
        gp_normal.Transformed(loc.Transformation())
        normal = geom_utils.gp_to_numpy(gp_normal)
        if self.reversed():
            normal = -normal
        return normal

    def is_left_of(self, edge):
        """
        Is this face on the left hand side of the given edge.   We take the 
        orientation of the edge into account here

                     Edge direction
                            ^
                            |   
                  Left      |   Right 
                  face      |   face
                            |
        Args:
            edge (occwl.edge.Edge): Edge

        Returns:
            bool: True if the face is to the left of the edge
        """
        found_edge = False
        for wire in self.wires():
            for edge_from_face in wire.ordered_edges():
                if edge == edge_from_face:
                    if edge.reversed() == edge_from_face.reversed():
                        return True
                    else:
                        # We found the edge, but so far we only found an edge
                        # with orientation such that the face is on the right
                        found_edge = True

        # If we didn't find the edge at all then this function was used incorrectly.
        # To use it you need to pass in a edge around the given face.  Assert and warn 
        # the user
        assert found_edge, "Edge doesn't belong to face"

        # We found an edge for which this face was on the right hand side,
        # but not one of the left hand side
        return False

    def gaussian_curvature(self, uv):
        """
        Compute the gaussian curvature of the surface geometry at given parameter

        Args:
            uv (np.ndarray or tuple): Surface parameter

        Returns:
            float: Gaussian curvature
        """
        return GeomLProp_SLProps(
            self.surface(), uv[0], uv[1], 2, 1e-9
        ).GaussianCurvature()

    def min_curvature(self, uv):
        """
        Compute the minimum curvature of the surface geometry at given parameter

        Args:
            uv (np.ndarray or tuple): Surface parameter

        Returns:
            float: Min. curvature
        """
        min_curv = GeomLProp_SLProps(
            self.surface(), uv[0], uv[1], 2, 1e-9
        ).MinCurvature()
        if self.reversed():
            min_curv *= -1
        return min_curv

    def mean_curvature(self, uv):
        """
        Compute the mean curvature of the surface geometry at given parameter

        Args:
            uv (np.ndarray or tuple): Surface parameter

        Returns:
            float: Mean curvature
        """
        mean_curv = GeomLProp_SLProps(
            self.surface(), uv[0], uv[1], 2, 1e-9
        ).MeanCurvature()
        if self.reversed():
            mean_curv *= -1
        return mean_curv

    def max_curvature(self, uv):
        """
        Compute the maximum curvature of the surface geometry at given parameter

        Args:
            uv (np.ndarray or tuple): Surface parameter

        Returns:
            float: Max. curvature
        """
        max_curv = GeomLProp_SLProps(
            self.surface(), uv[0], uv[1], 2, 1e-9
        ).MaxCurvature()
        if self.reversed():
            max_curv *= -1
        return max_curv

    def pcurve(self, edge):
        """
        Get the given edge's curve geometry as a 2D parametric curve
        on this face

        Args:
            edge (occwl.edge.Edge): Edge

        Returns:
            Geom2d_Curve: 2D curve
            Interval: domain of the parametric curve
        """
        crv, umin, umax = BRep_Tool().CurveOnSurface(
            edge.topods_shape(), self.topods_shape()
        )
        return crv, Interval(umin, umax)

    def uv_bounds(self):
        """
        Get the UV-domain bounds of this face's surface geometry

        Returns:
            Box: UV-domain bounds
        """
        umin, umax, vmin, vmax = breptools_UVBounds(self.topods_shape())
        bounds = Box(np.array([umin, vmin]))
        bounds.encompass_point(np.array([umax, vmax]))
        return bounds

    def point_to_parameter(self, pt):
        """
        Get the UV parameter by projecting the point on this face

        Args:
            pt (np.ndarray): 3D point

        Returns:
            np.ndarray: UV-coordinate
        """
        loc = TopLoc_Location()
        surf = BRep_Tool_Surface(self.topods_shape(), loc)
        gp_pt = gp_Pnt(pt[0], pt[1], pt[2])
        inv = loc.Transformation().Inverted()
        gp_pt.Transformed(inv)
        uv = ShapeAnalysis_Surface(surf).ValueOfUV(
            gp_pt, 1e-9
        )
        return np.array(uv.Coord())

    def surface_type(self):
        """
        Get the type of the surface geometry

        Returns:
            str: Type of the surface geometry
        """
        surf_type = BRepAdaptor_Surface(self.topods_shape()).GetType()
        if surf_type == GeomAbs_Plane:
            return "plane"
        if surf_type == GeomAbs_Cylinder:
            return "cylinder"
        if surf_type == GeomAbs_Cone:
            return "cone"
        if surf_type == GeomAbs_Sphere:
            return "sphere"
        if surf_type == GeomAbs_Torus:
            return "torus"
        if surf_type == GeomAbs_BezierSurface:
            return "bezier"
        if surf_type == GeomAbs_BSplineSurface:
            return "bspline"
        if surf_type == GeomAbs_SurfaceOfRevolution:
            return "revolution"
        if surf_type == GeomAbs_SurfaceOfExtrusion:
            return "extrusion"
        if surf_type == GeomAbs_OffsetSurface:
            return "offset"
        if surf_type == GeomAbs_OtherSurface:
            return "other"
        return "unknown"
    
    def surface_type_enum(self):
        """
        Get the type of the surface geometry as an OCC.Core.GeomAbs enum

        Returns:
            OCC.Core.GeomAbs: Type of the surface geometry
        """
        return BRepAdaptor_Surface(self.topods_shape()).GetType()

    def closed_u(self):
        """
        Whether the surface is closed along the U-direction

        Returns:
            bool: Is closed along U
        """
        sa = ShapeAnalysis_Surface(self.surface())
        return sa.IsUClosed()

    def closed_v(self):
        """
        Whether the surface is closed along the V-direction

        Returns:
            bool: Is closed along V
        """
        sa = ShapeAnalysis_Surface(self.surface())
        return sa.IsVClosed()

    def periodic_u(self):
        """
        Whether the surface is periodic along the U-direction

        Returns:
            bool: Is periodic along U
        """
        adaptor = BRepAdaptor_Surface(self.topods_shape())
        return adaptor.IsUPeriodic()

    def periodic_v(self):
        """
        Whether the surface is periodic along the V-direction

        Returns:
            bool: Is periodic along V
        """
        adaptor = BRepAdaptor_Surface(self.topods_shape())
        return adaptor.IsVPeriodic()

    def get_triangles(self, return_normals=False):
        """
        Get the tessellation of this face as a triangle mesh
        NOTE: First you must call shape.triangulate_all_faces()
        Then call this method to get the triangles for the
        face.

        Args:
            return_normals (bool): Return vertex normals

        Returns:
            2D np.ndarray: Vertices
            2D np.ndarray: Faces
            2D np.ndarray: Vertex Normals (when return_normals is True)
        """
        location = TopLoc_Location()
        bt = BRep_Tool()
        facing = bt.Triangulation(self.topods_shape(), location)
        if facing == None:
            if return_normals:
                return (
                    np.empty(shape=(0,3), dtype=np.float32),
                    np.empty(shape=(0,3), dtype=np.int32),
                    np.empty(shape=(0,3), dtype=np.float32)
                )
            else:
                return (
                    np.empty(shape=(0,3), dtype=np.float32),
                    np.empty(shape=(0,3), dtype=np.int32)
                )

        vert_nodes = facing.Nodes()
        tri = facing.Triangles()
        uv_nodes = facing.UVNodes()
        verts = []
        normals = []
        for i in range(1, facing.NbNodes() + 1):
            vert = vert_nodes.Value(i).Transformed(location.Transformation())
            verts.append(np.array(list(vert.Coord())))
            if return_normals:
                uv = uv_nodes.Value(i).Coord()
                normal = self.normal(uv)
                normals.append(normal)

        tris = []
        reversed = self.reversed()
        for i in range(1, facing.NbTriangles() + 1):
            # OCC triangle normals point in the surface normal
            # direction
            if reversed:
                index1, index3, index2 = tri.Value(i).Get()
            else:
                index1, index2, index3 = tri.Value(i).Get()

            tris.append([index1 - 1, index2 - 1, index3 - 1])

        np_verts = np.asarray(verts, dtype=np.float32)
        np_tris = np.asarray(tris, dtype=np.int32)

        if return_normals:
            np_normals = np.asarray(normals, dtype=np.float32)
            return np_verts, np_tris, np_normals
        else:
            return np_verts, np_tris
