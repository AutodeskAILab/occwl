# System
import numpy as np

# OCC
from occwl.compound import Compound

# Test
from tests.test_base import TestBase


class FaceTester(TestBase):
    def test_face(self):
        data_folder = self.test_folder() / "test_data"
        self.run_test_on_all_files_in_folder(data_folder)

    def test_get_triangles(self):
        """ Test getting triangles from a face """
        # Test a single block
        block_file = self.test_folder() / "test_data/block.step"
        solids = list(Compound.load_from_step(block_file).solids())
        for solid in solids:
            solid.triangulate_all_faces()
            faces = solid.faces()
            for face in faces:
                # Check getting triangles without normals
                verts, tris = face.get_triangles()
                self.assertIsInstance(verts, np.ndarray)
                self.assertIsInstance(tris, np.ndarray)
                self.assertEqual(verts.shape[1], 3)
                self.assertEqual(tris.shape[1], 3)
                # Check getting triangles with normals
                verts, tris, normals = face.get_triangles(return_normals=True)
                self.assertIsInstance(normals, np.ndarray)
                self.assertEqual(normals.shape[1], 3)
                # Check the normals are close to 1.0 length
                lengths = np.linalg.norm(normals, axis=1)
                self.assertTrue(np.allclose(lengths, np.ones(lengths.shape)))
                # Test the values of the normals of the six sides of the block
                # Top of block - assuming Y-Up
                if np.all(np.isclose(verts[:,1], 50)):
                    # Point up along Y
                    self.assertTrue(np.all(np.isclose(normals[:,1], 1)))
                # Bottom of block
                elif np.all(np.isclose(verts[:,1], 0)):
                    # Point down along Y
                    self.assertTrue(np.all(np.isclose(normals[:,1], -1)))
                # Vertical side
                elif np.all(np.isclose(verts[:,0], 50)):
                    # Point out from X
                    self.assertTrue(np.all(np.isclose(normals[:,0], 1)))                    
                # Vertical side
                elif np.all(np.isclose(verts[:,0], 0)):
                    # Point back from X
                    self.assertTrue(np.all(np.isclose(normals[:,0], -1)))   
                # Vertical side
                elif np.all(np.isclose(verts[:,2], 40)):
                    # Point out from Z
                    self.assertTrue(np.all(np.isclose(normals[:,2], 1)))
                # Vertical side
                elif np.all(np.isclose(verts[:,2], 0)):
                    # Point back from Z
                    self.assertTrue(np.all(np.isclose(normals[:,2], -1)))                                                         

    def perform_is_left_of_test(self, solid):
        for face in solid.faces():
            for wire in face.wires():
                for edge in wire.ordered_edges():
                    self.assertTrue(face.is_left_of(edge))

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

        closed_u, closed_v = face.closed_u(), face.closed_v()
        self.assertTrue(isinstance(closed_u, bool))
        self.assertTrue(isinstance(closed_v, bool))

        periodic_u, periodic_v = face.periodic_u(), face.periodic_v()
        self.assertTrue(isinstance(periodic_u, bool))
        self.assertTrue(isinstance(periodic_v, bool))

        curv_g = face.gaussian_curvature(uv)
        self.assertTrue(isinstance(curv_g, float))
        curv_g_rev = face.reversed_face().gaussian_curvature(uv)
        self.assertTrue(np.allclose(curv_g, curv_g_rev))

        curv_max = face.max_curvature(uv)
        self.assertTrue(isinstance(curv_max, float))
        curv_max_rev = face.reversed_face().max_curvature(uv)
        self.assertTrue(np.allclose(curv_max, -curv_max_rev))

        curv_min = face.min_curvature(uv)
        self.assertTrue(isinstance(curv_min, float))
        curv_min_rev = face.reversed_face().min_curvature(uv)
        self.assertTrue(np.allclose(curv_min, -curv_min_rev))

        curv_mean = face.mean_curvature(uv)
        self.assertTrue(isinstance(curv_mean, float))
        curv_mean_rev = face.reversed_face().mean_curvature(uv)
        self.assertTrue(np.allclose(curv_mean, -curv_mean_rev))

        area = face.area()
        self.assertTrue(isinstance(area, float))

        reversed_face = face.reversed_face()
        self.assertTrue(type(face) == type(reversed_face))
        self.assertTrue(face.reversed() != reversed_face.reversed())

    def run_test(self, solid):
        self.perform_is_left_of_test(solid)
        faces = solid.faces()
        for face in faces:
            self.perform_tests_on_face(face)
