import numpy as np

from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pnt2d
from OCC.Core.BRepTools import breptools_UVBounds
from OCC.Core.TopAbs import TopAbs_IN, TopAbs_REVERSED
from OCC.Core.BRepTopAdaptor import BRepTopAdaptor_FClass2d
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRep import BRep_Tool_Surface
from OCC.Core.GeomLProp import GeomLProp_SLProps
from OCC.Core.ShapeAnalysis import ShapeAnalysis_Surface
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder, GeomAbs_Cone, GeomAbs_Sphere, GeomAbs_Torus, GeomAbs_BezierSurface, GeomAbs_BSplineSurface
from OCC.Extend import TopologyUtils
from OCC.Core.TopoDS import TopoDS_Face
from OCC.Core.TopLoc import TopLoc_Location

import geometry.geom_utils as geom_utils
from geometry.box import Box

class Face:
    def __init__(self, topods_face):
        assert isinstance(topods_face, TopoDS_Face)
        self._face = topods_face
        self._trimmed = BRepTopAdaptor_FClass2d(self._face, 1e-9)
    
    def hash(self):
        return hash(self.topods_face())

    def inside(self, uv):
        result = self._trimmed.Perform(gp_Pnt2d(uv[0], uv[1]))
        return result == TopAbs_IN

    def surface(self):
        return BRep_Tool_Surface(self._face)
    
    def specific_surface(self):
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
            return srf.BSplineSurface()
        raise ValueError("Unknown surface type: ", surf_type)

    def reversed(self):
        """
        Returns if the orientation of the face is reversed i.e. TopAbs_REVERSED
        """
        return self._face.Orientation() == TopAbs_REVERSED

    def point(self, uv):
        pt = self.surface().Value(uv[0], uv[1])
        return geom_utils.gp_to_numpy(pt)

    def tangent(self, uv):
        dU, dV = gp_Dir(), gp_Dir()
        res = GeomLProp_SLProps(self.surface(), uv[0], uv[1], 1, 1e-9)
        if res.IsTangentUDefined() and res.IsTangentVDefined():
            res.TangentU(dU), res.TangentV(dV)
            return (geom_utils.gp_to_numpy(dU)), (geom_utils.gp_to_numpy(dV))
        return None, None

    def normal(self,uv):
        res = GeomLProp_SLProps(self.surface(), uv[0], uv[1], 1, 1e-9)
        if not res.IsNormalDefined():
            return (0, 0, 0)
        normal = geom_utils.gp_to_numpy(res.Normal())
        if self.reversed():
            normal = -normal
        return normal

    def gaussian_curvature(self, uv):
        return GeomLProp_SLProps(self.surface(), uv[0], uv[1], 2, 1e-9).GaussianCurvature()

    def min_curvature(self, uv):
        min_curv = GeomLProp_SLProps(self.surface(), uv[0], uv[1], 2, 1e-9).MinCurvature()
        if self.reversed():
            min_curv *= -1
        return min_curv

    def mean_curvature(self, uv):
        return GeomLProp_SLProps(self.surface(), uv[0], uv[1], 2, 1e-9).MeanCurvature()

    def max_curvature(self, uv):
        max_curv = GeomLProp_SLProps(self.surface(), uv[0], uv[1], 2, 1e-9).MaxCurvature()
        if self.reversed():
            max_curv *= -1
        return max_curv

    def area(self):
        pass

    def uv_bounds(self):
        umin, umax, vmin, vmax = breptools_UVBounds(self._face)
        bounds = Box(np.array([umin, vmin]))
        bounds.encompass_point(np.array([umax, vmax]))
        return bounds
    
    def point_to_parameter(self, pt):
        uv = ShapeAnalysis_Surface(self.surface()).ValueOfUV(gp_Pnt(pt[0], pt[1], pt[2]), 1e-9)
        return uv.Coord()

    def surface_type(self):
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
        return self._face


    def get_triangles(self):
        """
        First you must call solid.triangulate_all_faces()
        Then call this method to get the triangles for the
        face.
        """
        location = TopLoc_Location()
        bt = BRep_Tool()
        facing = (bt.Triangulation(self._face, location))
        if facing == None:
            return None

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