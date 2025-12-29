# System
import numpy as np

# OCC
from OCC.Core.gp import gp_Pnt
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Extend.ShapeFactory import point_list_to_TColgp_Array1OfPnt

# occwl
from occwl.geometry.interval import Interval
from occwl.edge import Edge
from occwl.geometry.arc_length_param_finder import ArcLengthParamFinder


# Test
from tests.test_base import TestBase


class ArcLengthParamFinderTester(TestBase):
    def test_arc_length_param_finder(self):
        # Create an edge with a non-linear parametrization
        array = []
        array.append(gp_Pnt(0, 0, 0))
        array.append(gp_Pnt(0, 0, 0))
        array.append(gp_Pnt(20, 0, 0))
        array.append(gp_Pnt(0, 0, 0))
        array.append(gp_Pnt(0, 0, 0))

        pt_list1 = point_list_to_TColgp_Array1OfPnt(array)
        bspline = GeomAPI_PointsToBSpline(pt_list1).Curve()
        edge = Edge(BRepBuilderAPI_MakeEdge(bspline).Edge())

        arc_length_finder = ArcLengthParamFinder(edge=edge, num_arc_length_samples=100)
        us = arc_length_finder.find_arc_length_parameters(10)

        lengths = []
        interval = edge.u_bounds()
        last_u = None
        for u in us:
            if last_u is not None:
                lengths.append(self.find_arc_length(edge, last_u, u))
            last_u = u

        lengths = np.array(lengths)
        min_lengths = lengths.min()
        max_lengths = lengths.max()
        length_deviation = max_lengths - min_lengths
        eps = 5e-2
        self.assertLess(length_deviation, eps)

    def find_arc_length(self, edge, umin, umax):
        num_samples = 1000
        interval = Interval(umin, umax)
        points = []
        for i in range(num_samples):
            t = i / (num_samples - 1)
            u = interval.interpolate(t)
            points.append(edge.point(u))
        length = 0
        last_point = None
        for point in points:
            if last_point is not None:
                length += np.linalg.norm(point - last_point)
            last_point = point
        return length
