import numpy as np

from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Vec, gp_Pnt2d
from OCC.Core.BRep import BRep_Tool_Curve, BRep_Tool_Continuity
from OCC.Core.GeomLProp import GeomLProp_SLProps
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.GeomAbs import GeomAbs_Line, GeomAbs_Circle, GeomAbs_Ellipse, GeomAbs_Hyperbola, GeomAbs_Parabola, GeomAbs_BezierCurve, GeomAbs_BSplineCurve, GeomAbs_OffsetCurve, GeomAbs_OtherCurve
from OCC.Core.TopAbs import TopAbs_REVERSED
from OCC.Extend import TopologyUtils
from OCC.Core.TopoDS import TopoDS_Edge
from OCC.Core.GCPnts import GCPnts_AbscissaPoint
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.ShapeAnalysis import ShapeAnalysis_Edge

import geometry.geom_utils as geom_utils
from geometry.interval import Interval

class Edge:
    def __init__(self, topods_edge):
        assert isinstance(topods_edge, TopoDS_Edge)
        self._edge = topods_edge
    
    def topods_edge(self):
        return self._edge

    def hash(self):
        return hash(self.topods_edge())
    
    def point(self, u):
        if self.has_curve():
            pt = self.curve().Value(u)
            return geom_utils.gp_to_numpy(pt)
        # If the edge has no curve then return a point
        # at the origin.
        # It would ne nice to return the location of the 
        # vertex
        return np.array([0,0,0])

    def tangent(self, u):
        if self.has_curve():
            pt = gp_Pnt()
            der = gp_Vec()
            self.curve().D1(u, pt, der)
            der.Normalize()
            tangent = geom_utils.gp_to_numpy(der)
            if self.reversed():
                tangent = -tangent
            return tangent
        # If the edge has no curve then return 
        # a zero vector
        return np.array([0,0,0])
    
    def first_derivative(self, u):
        if self.has_curve():
            pt = gp_Pnt()
            der = gp_Vec()
            self.curve().D1(u, pt, der)
            return geom_utils.gp_to_numpy(der)
        # If the edge has no curve then return 
        # a zero vector
        return np.array([0,0,0])

    def length(self, tolerance=1e-9):
        if not self.has_curve():
            return 0.0
        bounds = self.u_bounds()
        return GCPnts_AbscissaPoint().Length(
            BRepAdaptor_Curve(self.topods_edge()), 
            bounds.a, 
            bounds.b, 
            tolerance
        )

    def curve(self):
        return BRep_Tool_Curve(self._edge)[0]

    def specific_curve(self):
        brep_adaptor_curve = BRepAdaptor_Curve(self._edge)
        curv_type = brep_adaptor_curve.GetType()
        if curv_type == GeomAbs_Line:
            return brep_adaptor_curve.Line()
        if curv_type == GeomAbs_Circle:
            return brep_adaptor_curve.Circle()
        if curv_type == GeomAbs_Ellipse:
            return brep_adaptor_curve.Ellipse()
        if curv_type == GeomAbs_Hyperbola:
            return brep_adaptor_curve.Hyperbola()
        if curv_type == GeomAbs_Parabola:
            return brep_adaptor_curve.Parabola()
        if curv_type == GeomAbs_BezierCurve:
            return brep_adaptor_curve.BezierCurve()
        if curv_type == GeomAbs_BSplineCurve:
            return brep_adaptor_curve.BSplineCurve()
        if curv_type == GeomAbs_OffsetCurve:
            return brep_adaptor_curve.OffsetCurve()
        raise ValueError("Unknown curve type: ", curv_type)

    def has_curve(self):
        """
        Does this edge have a valid curve?
        Some edges don't.  For example the edge at the pole of a sphere.
        """
        curve = BRepAdaptor_Curve(self.topods_edge())
        return curve.Is3DCurve() 


    def u_bounds(self):
        if not self.has_curve():
            # Return an empty interval
            return Interval()
        _, umin, umax = BRep_Tool_Curve(self.topods_edge())
        return Interval(umin, umax)
    
    def twin_edge(self):
        pass

    def convex(self):
        """
        Returns the convex flag associated with the edge
        NOTE: this does not check for edge convexity
        """
        return self.topods_edge().Convex()
    
    def closed(self):
        return self.topods_edge().Closed()

    def seam(self, face):
        return ShapeAnalysis_Edge().IsSeam(self.topods_edge(), face.topods_face())

    def periodic(self):
        return BRepAdaptor_Curve(self.topods_edge()).IsPeriodic()

    def rational(self):
        return BRepAdaptor_Curve(self.topods_edge()).IsRational()

    def continuity(self, face1, face2):
        return BRep_Tool_Continuity(self.topods_edge(), face1.topods_face(), face2.topods_face())

    def reversed(self):
        return self.topods_edge().Orientation() == TopAbs_REVERSED
    
    def curve_type(self):
        curv_type = BRepAdaptor_Curve(self._edge).GetType()
        if curv_type == GeomAbs_Line:
            return "line"
        if curv_type == GeomAbs_Circle:
            return "circle"
        if curv_type == GeomAbs_Ellipse:
            return "ellipse"
        if curv_type == GeomAbs_Hyperbola:
            return "hyperbola"
        if curv_type == GeomAbs_Parabola:
            return "parabola"
        if curv_type == GeomAbs_BezierCurve:
            return "bezier"
        if curv_type == GeomAbs_BSplineCurve:
            return "bspline"
        if curv_type == GeomAbs_OffsetCurve:
            return "offset"
        if curv_type == GeomAbs_OtherCurve:
            return "other"
        return "unknown"
