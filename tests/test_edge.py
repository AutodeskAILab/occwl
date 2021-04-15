
# System
import numpy as np

# Geometry
from geometry.interval import Interval

# Test
from test_base import TestBase

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
            t = i/(num_samples-1)
            pt = edge.point(t)
            self.assertTrue(isinstance(pt, np.ndarray))
            tangent = edge.tangent(t)
            self.assertTrue(isinstance(tangent, np.ndarray))
            d1 = edge.first_derivative(t)
            self.assertTrue(isinstance(d1, np.ndarray))

        concave = edge.convex()
        self.assertTrue(isinstance(concave, bool))
        closed = edge.closed()
        self.assertTrue(isinstance(closed, bool))
        periodic = edge.periodic()
        self.assertTrue(isinstance(periodic, bool))
        rational = edge.rational()
        self.assertTrue(isinstance(rational, bool))
        reversed = edge.reversed()
        self.assertTrue(isinstance(reversed, bool))
        curve_type = edge.curve_type()
        self.assertTrue(isinstance(curve_type, str))

    def run_test(self, solid):
        edges = solid.edges()
        for edge in edges:
            self.perform_tests_on_edge(edge)
