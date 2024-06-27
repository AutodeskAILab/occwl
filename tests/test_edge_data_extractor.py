# System
import numpy as np
import sys

# OCC
from OCC.Core.Quantity import (
    Quantity_Color,
    Quantity_TOC_RGB,
    Quantity_NOC_WHITE,
    Quantity_NOC_BLACK,
    Quantity_NOC_BLUE1,
    Quantity_NOC_CYAN1,
    Quantity_NOC_RED,
    Quantity_NOC_GREEN,
    Quantity_NOC_ORANGE,
    Quantity_NOC_YELLOW,
)


# occwl
from occwl.edge_data_extractor import EdgeDataExtractor, EdgeConvexity
from occwl.compound import Compound
from occwl.viewer import Viewer

# Test
from tests.test_base import TestBase


class EdgeDataExtractorTester(TestBase):
    def check_edges(self, filename, edge_checks_list):
        # Load the solid
        solid_pathname = self.test_folder() / "test_data" / filename
        self.assertTrue(solid_pathname.exists())
        solids = list(Compound.load_from_step(solid_pathname).solids())
        self.assertEqual(len(solids), 1)
        solid = solids[0]

        # Test that the extractor doesn't crash
        self.check_extract_data_for_all_edges(solid)

        # Uncomment here to view the convexities of all edges
        # in the solid
        # self.visualize_edge_convexities(solid)

        for edge_checks in edge_checks_list:
            # Find the edge
            datum = np.array(edge_checks["datum"])
            edge = solid.find_closest_edge_slow(datum)

            # Run the checks
            self.check_edge(datum, edge, solid, edge_checks)

    def check_normals(self, datum, expected_normals, extractor):
        num_samples = extractor.points.shape[0]
        closest_normals = self.find_closest_normals_to_datum(datum, extractor)
        for expected_normal in expected_normals:
            expected_num_occurrences = expected_normal["num_occurrences"]
            expected_normal = np.array(expected_normal["vector"])

            found_num_occurrences = 0
            for normal in closest_normals:
                # Make sure the angle tolerance for the normals is big enough
                # If we polygonize the curve with num_samples points then we have
                # num_samples-1 spans.
                normal_angle_tol = 2 * 3.141 / (num_samples - 1)
                angle_rads = self.angle_between_vectors(normal, expected_normal)
                if angle_rads < normal_angle_tol:
                    found_num_occurrences += 1
            self.assertEqual(expected_num_occurrences, found_num_occurrences)

    def check_edge(self, datum, edge, solid, edge_checks):
        faces = list(solid.faces_from_edge(edge))
        num_samples = 12
        extractor_arc_length = EdgeDataExtractor(
            edge, faces, num_samples, use_arclength_params=True
        )
        self.assertEqual(extractor_arc_length.points.shape[0], num_samples)
        self.assertEqual(extractor_arc_length.tangents.shape[0], num_samples)
        self.assertEqual(extractor_arc_length.left_normals.shape[0], num_samples)
        self.assertEqual(extractor_arc_length.right_normals.shape[0], num_samples)
        self.assertTrue(extractor_arc_length.good)
        self.sanity_check_uvs_for_watertight_edge(edge, extractor_arc_length)

        extractor_uniform = EdgeDataExtractor(
            edge, faces, num_samples, use_arclength_params=False
        )
        self.assertEqual(extractor_arc_length.points.shape[0], num_samples)
        self.assertEqual(extractor_uniform.tangents.shape[0], num_samples)
        self.assertEqual(extractor_uniform.left_normals.shape[0], num_samples)
        self.assertEqual(extractor_uniform.right_normals.shape[0], num_samples)
        self.assertTrue(extractor_uniform.good)
        self.sanity_check_uvs_for_watertight_edge(edge, extractor_uniform)

        angle_tol_rads = 0.0872664626  # 5 degrees
        if "expected_convexity" in edge_checks:
            expected_convexity = edge_checks["expected_convexity"]

            convexity_uniform = extractor_uniform.edge_convexity(angle_tol_rads)
            self.assertEqual(convexity_uniform, expected_convexity)

            convexity_arclength = extractor_arc_length.edge_convexity(angle_tol_rads)
            self.assertEqual(convexity_arclength, expected_convexity)

        if "normals" in edge_checks:
            self.check_normals(datum, edge_checks["normals"], extractor_uniform)
            self.check_normals(datum, edge_checks["normals"], extractor_arc_length)

    def find_closest_normals_to_datum(self, datum, extractor):
        normals = []
        index = self.find_closest_index_to_datum(datum, extractor)
        normals.append(extractor.left_normals[index])
        normals.append(extractor.right_normals[index])
        return normals

    def find_closest_index_to_datum(self, datum, extractor):
        best_dist_yet = sys.float_info.max
        best_index_yet = None
        for index, point in enumerate(extractor.points):
            dist = np.linalg.norm(point - datum)
            if dist < best_dist_yet:
                best_dist_yet = dist
                best_index_yet = index
        return best_index_yet

    def sanity_check_uvs_for_watertight_edge(self, edge, extractor):
        # Test here on watertight models to make sure
        # that the uvs we found are parameterized in the
        # same way as the 3d curve

        # Looks like Open Cascade isn't accurate enough to stay inside
        # its edge tol limits
        big_tol = 1e-3 + edge.tolerance()
        extractor.sanity_check_uvs(extractor.left_uvs, big_tol)
        extractor.sanity_check_uvs(extractor.right_uvs, big_tol)

    def test_on_block(self):
        edge_checks_list = [
            {
                "datum": [25.000000, 0.000000, 40.000000],
                "expected_convexity": EdgeConvexity.CONVEX,
                "normals": [
                    {"num_occurrences": 1, "vector": [0, 0, 1]},
                    {"num_occurrences": 1, "vector": [0, -1, 0]},
                ],
            }
        ]
        self.check_edges("block.step", edge_checks_list)

    def test_on_block_fillet1(self):
        edge_checks_list = [
            {
                "datum": [0.000000, 32.500000, 40.000000],
                "expected_convexity": EdgeConvexity.CONVEX,
                "normals": [
                    {"num_occurrences": 1, "vector": [-1, 0, 0]},
                    {"num_occurrences": 1, "vector": [0, 0, 1]},
                ],
            },
            {
                "datum": [25.000000, 15.000000, 40.000000],
                "expected_convexity": EdgeConvexity.SMOOTH,
                "normals": [{"num_occurrences": 2, "vector": [0, 0, 1]}],
            },
            {
                "datum": [25.000000, 0.000000, 25.000000],
                "expected_convexity": EdgeConvexity.SMOOTH,
                "normals": [{"num_occurrences": 2, "vector": [0, -1, 0]}],
            },
        ]
        self.check_edges("block_fillet1.step", edge_checks_list)

    def test_on_block_fillet3(self):
        edge_checks_list = [
            {
                "datum": [35.000000, 4.393398, 35.606602],
                "expected_convexity": EdgeConvexity.SMOOTH,
                "normals": [{"num_occurrences": 2, "vector": [0, -1, 1]}],
            }
        ]
        self.check_edges("block_fillet3.step", edge_checks_list)

    def test_on_block_hole(self):
        edge_checks_list = [
            {
                "datum": [16.893010, 26.381480, 30.000000],
                "expected_convexity": EdgeConvexity.CONVEX,
                "normals": [
                    {"num_occurrences": 1, "vector": [1, 0, 0]},
                    {"num_occurrences": 1, "vector": [0, 0, 1]},
                ],
            },
            {
                "datum": [25.000000, 18.274490, 20.000000],
                "expected_convexity": EdgeConvexity.CONCAVE,
                "normals": [
                    {"num_occurrences": 1, "vector": [0, 1, 0]},
                    {"num_occurrences": 1, "vector": [0, 0, 1]},
                ],
            },
        ]
        self.check_edges("Block_hole.step", edge_checks_list)

    def test_on_cylinder(self):
        edge_checks_list = [
            {
                "datum": [-20.000000, -0.000000, 40.000000],
                "expected_convexity": EdgeConvexity.CONVEX,
            }
        ]
        self.check_edges("cylinder.step", edge_checks_list)

    def test_on_sphere(self):
        edge_checks_list = [
            {
                "datum": [-20.000000, 0.000000, 0.000000],
                "expected_convexity": EdgeConvexity.SMOOTH,
            }
        ]
        self.check_edges("SingleSolidSphere.step", edge_checks_list)

    def test_on_three_concave_edge(self):
        edge_checks_list = [
            {
                "datum": [45.000000, 20.000000, 10.000000],
                "expected_convexity": EdgeConvexity.CONCAVE,
            },
            {
                "datum": [31.741849, 21.784541, 10.000000],
                "expected_convexity": EdgeConvexity.CONCAVE,
            },
            {
                "datum": [20.000000, 45.000000, 10.000000],
                "expected_convexity": EdgeConvexity.CONCAVE,
            },
        ]
        self.check_edges("three_concave_edge.step", edge_checks_list)

    def test_on_two_concave_closed_edge(self):
        edge_checks_list = [
            {
                "datum": [12.240761, 25.943958, 30.000000],
                "expected_convexity": EdgeConvexity.CONCAVE,
            },
            {
                "datum": [23.834680, 25.943958, 25.000000],
                "expected_convexity": EdgeConvexity.CONCAVE,
            },
        ]
        self.check_edges("two_concave_closed_edge.step", edge_checks_list)

    def test_edge_with_transform(self):
        edge_checks_list = [
            {
                "datum": [70, 50, 40],
                "expected_convexity": EdgeConvexity.CONVEX,
            }
        ]
        self.check_edges("MovedBlock.step", edge_checks_list)

    def check_extract_data_for_all_edges(self, solid):
        for edge in solid.edges():
            faces = list(solid.faces_from_edge(edge))
            num_samples = 10
            extractor = EdgeDataExtractor(edge, faces, num_samples)
            if not extractor.good:
                # Skip polar edges
                continue

            # Here we just test that the extractor doesn't crash
            angle_tol_rads = 0.0872664626  # 5 degrees
            convexity = extractor.edge_convexity(angle_tol_rads)

    def visualize_edge_convexities(self, solid):
        v = Viewer()
        v.display(solid)
        for edge in solid.edges():
            faces = list(solid.faces_from_edge(edge))
            num_samples = 10
            extractor = EdgeDataExtractor(edge, faces, num_samples)
            if not extractor.good:
                # Skip polar edges
                continue
            angle_tol_rads = 0.0872664626  # 5 degrees
            convexity = extractor.edge_convexity(angle_tol_rads)
            if convexity == EdgeConvexity.CONCAVE:
                edge_color = Quantity_Color(Quantity_NOC_RED)
            elif convexity == EdgeConvexity.CONVEX:
                edge_color = Quantity_Color(Quantity_NOC_GREEN)
            elif convexity == EdgeConvexity.SMOOTH:
                edge_color = Quantity_Color(Quantity_NOC_BLUE1)
            else:
                self.fail("Unknown edge type")
            v.display(edge, color=edge_color)

        v.fit()
        v.show()
