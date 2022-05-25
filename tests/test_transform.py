"""
Test the transform() function
"""

# System
import numpy as np

from occwl.solid import Solid

# Test
from tests.test_base import TestBase

class TransformSolidTester(TestBase):
    def test_scale_solid(self):
        data_folder = self.test_folder() / "test_data"
        self.run_test_on_all_files_in_folder(data_folder)

    def run_test(self, solid):
        box = solid.exact_box()

        # Translate 1 model unit in x
        mat = np.array([
            [1, 0, 0, 1],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        transformed = solid.transform(mat)
        transformed_box = transformed.exact_box()

        tol = 0.01
        dxmin = transformed_box.intervals[0].a - box.intervals[0].a
        assert abs(dxmin -  1) < tol 

        dxmax = transformed_box.intervals[0].b - box.intervals[0].b
        assert abs(dxmax -  1) < tol 