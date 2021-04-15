
# System
import numpy as np

# Test
from test_base import TestBase

class FaceTester(TestBase):
        
    def test_face(self):
        data_folder = self.test_folder() / "test_data"
        self.run_test_on_all_files_in_folder(data_folder)

    def perform_tests_on_face(self, face):
        uv_box = face.uv_bounds()
        uv = uv_box.center()
        pt = face.point(uv)
        self.assertTrue(isinstance(pt, np.ndarray))

        surf = face.surface()
        if not surf.IsUPeriodic() and not surf.IsVPeriodic():
            uv_from_face = face.point_to_parameter(pt)
            self.assertTrue(np.allclose(uv, uv_from_face), 1e-2)

        tangent = face.tangent(uv)
        self.assertTrue(isinstance(tangent[0], np.ndarray))
        self.assertTrue(isinstance(tangent[1], np.ndarray))

        normal = face.normal(uv)
        self.assertTrue(isinstance(normal, np.ndarray))

        reversed = face.reversed()
        self.assertTrue(isinstance(reversed, bool))

        closed_u, closed_v = face.closed()
        self.assertTrue(isinstance(closed_u, bool))
        self.assertTrue(isinstance(closed_v, bool))

        periodic_u, periodic_v = face.periodic()
        self.assertTrue(isinstance(periodic_u, bool))
        self.assertTrue(isinstance(periodic_v, bool))

        curv_g = face.gaussian_curvature(uv)
        self.assertTrue(isinstance(curv_g, float))

        curv_max = face.max_curvature(uv)
        self.assertTrue(isinstance(curv_max, float))

        curv_min = face.min_curvature(uv)
        self.assertTrue(isinstance(curv_min, float))

        curv_mean = face.mean_curvature(uv)
        self.assertTrue(isinstance(curv_mean, float))

        area = face.area()
        self.assertTrue(isinstance(area, float))

    def run_test(self, solid):
        faces = solid.faces()
        for face in faces:
            self.perform_tests_on_face(face)
