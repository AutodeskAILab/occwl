import numpy as np

from occwl.vertex import Vertex

# Test
from tests.test_base import TestBase


class VertexTester(TestBase):
    def test_vertex(self):
        data_folder = self.test_folder() / "test_data"
        self.run_test_on_all_files_in_folder(data_folder)

    def perform_tests_on_vertex(self, vertex):
        reversed = vertex.reversed()
        self.assertTrue(isinstance(reversed, bool))
        pt = vertex.point()
        self.assertTrue(isinstance(pt, np.ndarray))

    def run_test(self, solid):
        for vertex in solid.vertices():
            self.perform_tests_on_vertex(vertex)