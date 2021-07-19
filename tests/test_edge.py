# System
import numpy as np

# Geometry
from occwl.geometry.interval import Interval
from OCC.Core.gp import gp_XOY, gp_Pnt
from OCC.Core.GC import GC_MakeSegment
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.Geom import Geom_Circle
from occwl.edge import Edge

# Test
from tests.test_base import TestBase


class EdgeTester(TestBase):
    def test_edge(self):
        data_folder = self.test_folder() / "test_data"
        self.run_test_on_all_files_in_folder(data_folder)

    def perform_tests_on_edge(self, edge):
        curve = edge.curve()
        self.assertTrue(curve is not None)

        # Can't do this test as we have some unsupported curve types
        # specific_curve = edge.specific_curve()
        # self.assertTrue(specific_curve is not None)

        length = edge.length()
        self.assertGreaterEqual(length, 0)

        bound = edge.u_bounds()
        self.assertTrue(isinstance(bound, Interval))

        num_samples = 10
        for i in range(num_samples):
            t = i / (num_samples - 1)
            pt = edge.point(t)
            self.assertTrue(isinstance(pt, np.ndarray))
            tangent = edge.tangent(t)
            self.assertTrue(isinstance(tangent, np.ndarray))
            d1 = edge.first_derivative(t)
            self.assertTrue(isinstance(d1, np.ndarray))

        self._test_closed_periodic()
        rational = edge.rational()
        self.assertTrue(isinstance(rational, bool))
        reversed = edge.reversed()
        self.assertTrue(isinstance(reversed, bool))
        self._test_curve_type()
        self._test_specific_curve(edge)

    def test_closed(self):
        block_hole = self.load_single_solid_from_test_data("Block_hole.step")
        closed_edge = block_hole.find_closest_edge_slow(
            np.array([16.893010, 26.381480, 20.000000])
        )
        self.assertTrue(closed_edge.closed_edge())
        self.assertTrue(closed_edge.closed_curve())

        fillet1 = self.load_single_solid_from_test_data("block_fillet1.step")
        closed_curve_edge = fillet1.find_closest_edge_slow(
            np.array([0.000000, 4.393398, 35.606602])
        )
        self.assertFalse(closed_curve_edge.closed_edge())
        self.assertTrue(closed_curve_edge.closed_curve())

    def _test_closed_periodic(self):
        # Circle
        circle = BRepBuilderAPI_MakeEdge(Geom_Circle(gp_XOY(), 1)).Edge()
        circle = Edge(circle)
        is_closed = circle.closed_curve()
        is_periodic = circle.periodic()
        self.assertTrue(isinstance(is_closed, bool))
        self.assertTrue(isinstance(is_periodic, bool))
        self.assertTrue(is_closed)
        self.assertTrue(is_periodic)
        # Line segment
        line = BRepBuilderAPI_MakeEdge(
            GC_MakeSegment(gp_Pnt(0, 0, 0), gp_Pnt(1, 1, 1)).Value()
        ).Edge()
        line = Edge(line)
        is_closed = line.closed_curve()
        is_periodic = line.periodic()
        self.assertTrue(not is_closed)
        self.assertTrue(not is_periodic)

    def _test_curve_type(self):
        circle = BRepBuilderAPI_MakeEdge(Geom_Circle(gp_XOY(), 1)).Edge()
        circle = Edge(circle)
        curve_type = circle.curve_type()
        self.assertTrue(isinstance(curve_type, str))
        self.assertTrue(curve_type == "circle")

    def _test_specific_curve(self, edge):
        if edge.has_curve():
            crv = edge.specific_curve()
            self.assertTrue(crv is not None)

    def run_test(self, solid):
        edges = solid.edges()
        for edge in edges:
            self.perform_tests_on_edge(edge)
