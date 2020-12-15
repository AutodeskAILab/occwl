from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pnt2d
from OCC.Core.BRepTools import breptools_UVBounds
from OCC.Core.TopAbs import TopAbs_IN, TopAbs_REVERSED
from OCC.Core.BRepTopAdaptor import BRepTopAdaptor_FClass2d
from OCC.Core.BRep import BRep_Tool_Surface
from OCC.Core.GeomLProp import GeomLProp_SLProps
from OCC.Core.ShapeAnalysis import ShapeAnalysis_Surface
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder, GeomAbs_Cone, GeomAbs_Sphere, GeomAbs_Torus, GeomAbs_BezierSurface, GeomAbs_BSplineSurface
from OCC.Extend import TopologyUtils
from OCC.Core.TopoDS import TopoDS_Face


class Face:
    def __init__(self, topods_face):
        assert isinstance(topods_face, TopoDS_Face)
        self._face = topods_face
        self._trimmed = BRepTopAdaptor_FClass2d(self._face, 1e-9)
    
    def hash(self):
        return hash(self.topods_face())

    def inside(self, u, v):
        result = self._trimmed.Perform(gp_Pnt2d(u, v))
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

    def point(self, u, v):
        pt = self.surface().Value(u, v)
        return (pt.X(), pt.Y(), pt.Z())

    def tangent(self, u, v):
        dU, dV = gp_Dir(), gp_Dir()
        res = GeomLProp_SLProps(self.surface(), u, v, 1, 1e-9)
        if res.IsTangentUDefined() and res.IsTangentVDefined():
            res.TangentU(dU), res.TangentV(dV)
            return (dU.X(), dU.Y(), dU.Z()), (dV.X(), dV.Y(), dV.Z())
        return None, None

    def normal(self, u, v):
        res = GeomLProp_SLProps(self.surface(), u, v, 1, 1e-9)
        if not res.IsNormalDefined():
            return (0, 0, 0)
        normal = (res.Normal().X(), res.Normal().Y(), res.Normal().Z())
        if self.reversed():
            normal = (-normal[0], -normal[1], -normal[2])
        return normal

    def gaussian_curvature(self, u, v):
        return GeomLProp_SLProps(self.surface(), u, v, 2, 1e-9).GaussianCurvature()

    def min_curvature(self, u, v):
        min_curv = GeomLProp_SLProps(self.surface(), u, v, 2, 1e-9).MinCurvature()
        if self.reversed():
            min_curv *= -1
        return min_curv

    def mean_curvature(self, u, v):
        return GeomLProp_SLProps(self.surface(), u, v, 2, 1e-9).MeanCurvature()

    def max_curvature(self, u, v):
        max_curv = GeomLProp_SLProps(self.surface(), u, v, 2, 1e-9).MaxCurvature()
        if self.reversed():
            max_curv *= -1
        return max_curv

    def area(self):
        pass

    def uv_bounds(self):
        return breptools_UVBounds(self._face)
    
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