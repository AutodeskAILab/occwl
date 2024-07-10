# System
import numpy as np

# OCC
from occwl.uvgrid import uvgrid, ugrid, _uvgrid_reverse_u

# Test
from tests.test_base import TestBase


class GridTester(TestBase):
    def test_grids_and_normals(self):
        data_folder = self.test_folder() / "test_data"
        self.run_test_on_all_files_in_folder(data_folder)

    def reverse_u_test(self, grid):
        reversed_grid = _uvgrid_reverse_u(grid)
        for i in range(grid.shape[0]):
            self.assertTrue((reversed_grid[i] == grid[grid.shape[0] - 1 - i]).all())

    def face_test(self, face):
        num_u = 10
        num_v = 10
        pts = uvgrid(face, num_u, num_v, method="point")
        nor = uvgrid(face, num_u, num_v, method="normal")
        length_eps = 1e-3
        if pts is not None and nor is not None:
            g = np.concatenate((pts, nor), axis=2)
            self.reverse_u_test(g)
            for i in range(1, num_u):
                for j in range(1, num_v):
                    pt00 = np.array(g[i - 1, j - 1, 0:3])
                    pt10 = np.array(g[i, j - 1, 0:3])
                    pt01 = np.array(g[i - 1, j, 0:3])
                    du = pt10 - pt00
                    dv = pt01 - pt00
                    approx_normal = np.cross(du, dv)
                    if np.linalg.norm(approx_normal) < length_eps:
                        # We can't do this test for very small vectors
                        continue
                    normal = np.array(g[i, j, 3:6])
                    angle = self.angle_between_vectors(approx_normal, normal)

                    angle_tol = np.pi / 4.0  # Big tol of 45 degrees
                    self.assertLess(angle, angle_tol)

    def edge_test(self, edge):
        num_u = 10
        pts = ugrid(edge, num_u, method="point")
        tgt = ugrid(edge, num_u, method="tangent")
        if pts is not None and tgt is not None:
            g = np.concatenate((pts, tgt), axis=1)
            for i in range(1, num_u):
                pt0 = np.array(g[i - 1, 0:3])
                pt1 = np.array(g[i, 0:3])
                du = pt1 - pt0
                tangent = np.array(g[i, 3:6])
                angle = self.angle_between_vectors(du, tangent)
                angle_tol = np.pi / 4.0  # Big tol of 45 degrees
                self.assertLess(angle, angle_tol)

    def run_test(self, solid):
        faces = solid.faces()
        for face in faces:
            self.face_test(face)

        edges = solid.edges()
        for edge in edges:
            self.edge_test(edge)
