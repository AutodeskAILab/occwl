import numpy as np

from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pnt2d
from OCC.Core.BRepTools import breptools_UVBounds
from OCC.Core.TopAbs import TopAbs_IN, TopAbs_REVERSED
from OCC.Core.BRepTopAdaptor import BRepTopAdaptor_FClass2d
from OCC.Core.BRepGProp import brepgprop_SurfaceProperties
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRep import BRep_Tool_Surface
from OCC.Core.GeomLProp import GeomLProp_SLProps
from OCC.Core.GProp import GProp_GProps
from OCC.Core.ShapeAnalysis import ShapeAnalysis_Surface
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder, GeomAbs_Cone, \
                             GeomAbs_Sphere, GeomAbs_Torus, GeomAbs_BezierSurface, \
                             GeomAbs_BSplineSurface, GeomAbs_SurfaceOfRevolution, \
                             GeomAbs_SurfaceOfExtrusion, GeomAbs_OffsetSurface, \
                             GeomAbs_OtherSurface
from OCC.Extend import TopologyUtils
from OCC.Core.TopoDS import TopoDS_Face
from OCC.Core.TopLoc import TopLoc_Location

import occwl.geometry.geom_utils as geom_utils
from occwl.geometry.box import Box

class Face:
    """
    A topological face in a solid model
    Represents a 3D surface bounded by a Wire
    """
    def __init__(self, topods_face):
        assert isinstance(topods_face, TopoDS_Face)
        self._face = topods_face
        self._trimmed = BRepTopAdaptor_FClass2d(self._face, 1e-9)
    
    def __hash__(self):
        """
        Hash for the face

        Returns:
            int: Hash value
        """
        return self.topods_face().__hash__()

    def inside(self, uv):
        """
        Check if the uv-coordinate in on the visible region of the face

        Args:
            uv (np.ndarray or tuple): Surface parameter
        
        Returns:
            bool: Is inside
        """
        result = self._trimmed.Perform(gp_Pnt2d(uv[0], uv[1]))
        return result == TopAbs_IN

    def surface(self):
        """
        Get the face surface geometry

        Returns:
            OCC.Geom.Handle_Geom_Surface: Interface to all surface geometry
        """
        return BRep_Tool_Surface(self._face)
    
    def specific_surface(self):
        """
        Get the specific face surface geometry

        Returns:
            OCC.Geom.Handle_Geom_*: Specific geometry type for the surface geometry
        """
        srf = BRepAdaptor_Surface(self._face)
        surf_type = self.surface_type()
        if surf_type == "plane":
            return srf.Plane()
        if surf_type == "cylinder":
            return srf.Cylinder()
        if surf_type == "torus":
            return srf.Torus()
        if surf_type == "bezier":
            return srf.BezierSurface()
        if surf_type == "bspline":
            return srf.BSpline()
        raise ValueError("Unknown surface type: ", surf_type)

    def reversed(self):
        """
        Returns if the orientation of the face is reversed i.e. TopAbs_REVERSED
        """
        return self._face.Orientation() == TopAbs_REVERSED

    def point(self, uv):
        """
        Evaluate the edge geometry at given parameter

        Args:
            uv (np.ndarray or tuple): Surface parameter
        
        Returns:
            np.ndarray: 3D Point
        """
        pt = self.surface().Value(uv[0], uv[1])
        return geom_utils.gp_to_numpy(pt)

    def tangent(self, uv):
        """
        Compute the tangents of the surface geometry at given parameter

        Args:
            uv (np.ndarray or tuple): Surface parameter

        Returns:
            Pair of np.ndarray or None: 3D unit vectors
        """
        dU, dV = gp_Dir(), gp_Dir()
        res = GeomLProp_SLProps(self.surface(), uv[0], uv[1], 1, 1e-9)
        if res.IsTangentUDefined() and res.IsTangentVDefined():
            res.TangentU(dU), res.TangentV(dV)
            return (geom_utils.gp_to_numpy(dU)), (geom_utils.gp_to_numpy(dV))
        return None, None

    def normal(self,uv):
        """
        Compute the normal of the surface geometry at given parameter

        Args:
            uv (np.ndarray or tuple): Surface parameter

        Returns:
            np.ndarray: 3D unit normal vector
        """
        res = GeomLProp_SLProps(self.surface(), uv[0], uv[1], 1, 1e-9)
        if not res.IsNormalDefined():
            return (0, 0, 0)
        normal = geom_utils.gp_to_numpy(res.Normal())
        if self.reversed():
            normal = -normal
        return normal

    def gaussian_curvature(self, uv):
        """
        Compute the gaussian curvature of the surface geometry at given parameter

        Args:
            uv (np.ndarray or tuple): Surface parameter

        Returns:
            float: Gaussian curvature
        """
        return GeomLProp_SLProps(self.surface(), uv[0], uv[1], 2, 1e-9).GaussianCurvature()

    def min_curvature(self, uv):
        """
        Compute the minimum curvature of the surface geometry at given parameter

        Args:
            uv (np.ndarray or tuple): Surface parameter

        Returns:
            float: Min. curvature
        """
        min_curv = GeomLProp_SLProps(self.surface(), uv[0], uv[1], 2, 1e-9).MinCurvature()
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
        mean_curv = GeomLProp_SLProps(self.surface(), uv[0], uv[1], 2, 1e-9).MeanCurvature()
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
        max_curv = GeomLProp_SLProps(self.surface(), uv[0], uv[1], 2, 1e-9).MaxCurvature()
        if self.reversed():
            max_curv *= -1
        return max_curv

    def area(self):
        """
        Compute the area of the face

        Returns:
            float: Area
        """
        geometry_properties = GProp_GProps()
        brepgprop_SurfaceProperties(self._face, geometry_properties)
        return geometry_properties.Mass()
    
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
        crv, umin, umax = BRep_Tool().CurveOnSurface(edge.topods_edge(), self.topods_face())
        return crv, Interval(umin, umax)

    def uv_bounds(self):
        """
        Get the UV-domain bounds of this face's surface geometry

        Returns:
            Box: UV-domain bounds
        """
        umin, umax, vmin, vmax = breptools_UVBounds(self._face)
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
        uv = ShapeAnalysis_Surface(self.surface()).ValueOfUV(gp_Pnt(pt[0], pt[1], pt[2]), 1e-9)
        return np.array(uv.Coord())

    def surface_type(self):
        """
        Get the type of the surface geometry

        Returns:
            str: Type of the surface geometry
        """
        surf_type = BRepAdaptor_Surface(self._face).GetType()
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

    def topods_face(self):
        """
        Get the underlying OCC face type

        Returns:
            OCC.Core.TopoDS.TopoDS_Face: Face
        """
        return self._face

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
        adaptor = BRepAdaptor_Surface(self._face)
        return adaptor.IsUPeriodic()
    
    def periodic_v(self):
        """
        Whether the surface is periodic along the V-direction

        Returns:
            bool: Is periodic along V
        """
        adaptor = BRepAdaptor_Surface(self._face)
        return adaptor.IsVPeriodic()

    def get_triangles(self):
        """
        Get the tessellation of this face as a triangle mesh
        NOTE: First you must call solid.triangulate_all_faces()
        Then call this method to get the triangles for the
        face.

        Returns:
            List[np.ndarray]: Vertices
            List[List]: Faces
        """
        location = TopLoc_Location()
        bt = BRep_Tool()
        facing = (bt.Triangulation(self._face, location))
        if facing == None:
            return [], []

        tab = facing.Nodes()
        tri = facing.Triangles()
        verts = []
        for i in range(1, facing.NbNodes()+1):
            verts.append(np.array(list(tab.Value(i).Coord())))

        tris = []
        reversed = self.reversed()
        for i in range(1, facing.NbTriangles()+1):
            # OCC triangle normals point in the surface normal
            # direction
            if reversed:
                index1, index3, index2 = tri.Value(i).Get()
            else:
                index1, index2, index3 = tri.Value(i).Get()

            tris.append([index1 - 1, index2 - 1, index3 - 1])
    
        return verts, tris