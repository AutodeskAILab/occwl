# System
import numpy as np

# Test
from tests.test_base import TestBase

class ScaleSolidTester(TestBase):
    def test_scale_solid(self):
        data_folder = self.test_folder() / "test_data"
        self.run_test_on_all_files_in_folder(data_folder)

    def run_test(self, solid):
        box = solid.exact_box()

        #scaled = scale_solid_to_unit_box(solid)
        scaled = solid.scale_to_unit_box()
        box_of_scaled = scaled.exact_box()

        center = box_of_scaled.center()
        origin = np.zeros(3)
        atol=1e-03
        self.assertTrue(np.allclose(center, origin, atol=atol))

        max_box_length = box_of_scaled.max_box_length()
        self.assertAlmostEqual(max_box_length, 2.0, delta=atol)


class SplitClosedFaceSolidTester(TestBase):
    def test_closed_face_split(self):
        data_folder = self.test_folder() / "test_data"
        self.run_test_on_all_files_in_folder(data_folder)

    def run_test(self, solid):
        num_original_faces = solid.num_faces()
        split_solid = solid.split_all_closed_faces(num_splits=1)
        self.assertTrue(split_solid is not None)
        num_faces_after_splitting = split_solid.num_faces()
        self.assertLessEqual(num_original_faces, num_faces_after_splitting)


class SplitClosedEdgeSolidTester(TestBase):
    def test_closed_edge_split(self):
        data_folder = self.test_folder() / "test_data"
        self.run_test_on_all_files_in_folder(data_folder)

    def run_test(self, solid):
        num_original_edges = solid.num_edges()
        split_solid = solid.split_all_closed_edges()
        self.assertTrue(split_solid is not None)
        num_edges_after_splitting = split_solid.num_edges()
        self.assertLessEqual(num_original_edges, num_edges_after_splitting)
