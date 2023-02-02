"""
Test for convert_geometric_identity_transforms_to_identity()
"""
# System
import numpy as np
from pathlib import Path

from occwl.compound import Compound

# Test
from tests.test_base import TestBase

class ConvertGeometricIdentity(TestBase):
    def test_convert_geometric_identity(self):
        files = [
            "tests/test_data/transform_tests/0153_003_final.step",
            "tests/test_data/transform_tests/0406_003_final.step"
        ]

        for file in files:
            compound = Compound.load_from_step(file)
            solids = list(compound.solids())
            for solid in solids:
                self.run_test(solid)

    def run_test(self, solid):
        solid.convert_geometric_identity_transforms_to_identity()
        self.assertTrue(solid.topods_shape().Location().IsIdentity())
        for face in solid.faces():
            surf = face.surface()
            surf = face.specific_surface()
            self.assertTrue(face.topods_shape().Location().IsIdentity())

        for edge in solid.edges():
            curve = edge.curve()
            curve = edge.specific_curve()
            self.assertTrue(edge.topods_shape().Location().IsIdentity())

        for vertex in solid.vertices():
            self.assertTrue(vertex.topods_shape().Location().IsIdentity())