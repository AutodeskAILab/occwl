
# System
import numpy as np

# occwl
from occwl.edge_data_extractor import EdgeDataExtractor, EdgeConvexity
from occwl.io import load_step

# Test
from test_base import TestBase


class EdgeDataExtractorTester(TestBase):

    def check_edges(self, filename, edge_checks_list):
        # Load the solid
        solid_pathname = self.test_folder() / "test_data" /filename
        self.assertTrue(solid_pathname.exists())
        solids = load_step(solid_pathname)
        self.assertEqual(len(solids), 1)
        solid = solids[0]
        
        for edge_checks in edge_checks_list:
            # Find the edge
            edge = solid.find_closest_edge_slow(np.array(edge_checks["datum"]))

            # Run the checks
            self.check_edge(edge, solid, edge_checks)

    def check_edge(self, edge, solid, edge_checks):
        faces = list(solid.faces_from_edge(edge))
        self.assertEqual(len(faces), 2)
        num_samples = 10
        extractor = EdgeDataExtractor(edge, faces[0], faces[1], num_samples)

        if "expected_convexity" in edge_checks:
            expected_convexity = edge_checks["expected_convexity"]

            angle_tol_rads = 0.0872664626 # 5 degrees
            convexity = extractor.edge_convexity(angle_tol_rads)
            self.assertEqual(convexity, expected_convexity)



    def test_on_block(self):
        edge_checks_list = [
            {
                "datum": [25.000000, 0.000000, 40.000000],
                "expected_convexity": EdgeConvexity.CONVEX,
                "normals": [
                    [0, 0, 1],
                    [0, -1, 0]
                ]
            }
        ]
        self.check_edges(
            "block.step",
            edge_checks_list
        )

    def test_on_block_fillet1(self):
        pass

    def test_on_block_fillet3(self):
        pass

    def test_on_block_hole(self):
        pass

    def test_on_cylinder(self):
        pass

    def test_on_sphere(self):
        pass

    def test_on_three_convex_edge(self):
        pass

    def test_on_two_convex_closed_edge(self):
        pass
