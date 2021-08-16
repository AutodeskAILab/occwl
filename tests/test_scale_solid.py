# System
import numpy as np

from occwl.scale_solid import scale_solid_to_unit_box

# Test
from tests.test_base import TestBase

class ScaleSolidTester(TestBase):
    def test_scale_solid(self):
        data_folder = self.test_folder() / "test_data"
        self.run_test_on_all_files_in_folder(data_folder)

    def run_test(self, solid):
        box = solid.exact_box()

        scaled = scale_solid_to_unit_box(solid)
        box_of_scaled = scaled.exact_box()

        center = box_of_scaled.center()
        origin = np.zeros(3)
        atol=1e-03
        self.assertTrue(np.allclose(center, origin, atol=atol))

        max_box_length = box_of_scaled.max_box_length()
        self.assertAlmostEqual(max_box_length, 2.0, delta=atol)
