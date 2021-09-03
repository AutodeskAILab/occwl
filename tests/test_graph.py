# System
import numpy as np

# Geometry
from occwl.geometry.interval import Interval
from OCC.Core.gp import gp_XOY, gp_Pnt
from OCC.Core.GC import GC_MakeSegment
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.Geom import Geom_Circle
from occwl.graph import vertex_adjacency, face_adjacency

# Test
from tests.test_base import TestBase


class GraphTester(TestBase):
    def test_solid(self):
        data_folder = self.test_folder() / "test_data"
        self.run_test_on_all_files_in_folder(data_folder)

    def perform_tests_on_solid(self, solid):
        if not solid.is_closed():
            print(f"Solid is not closed.  Skipping this example")
            return
        if not solid.check_unique_oriented_edges():
            print(f"Solid contains the same oriented edge twice.  Skipping this example")
            return

        # Vertex-adjacency graph
        vag = vertex_adjacency(solid)
        print(
            f"\tVertex Adjacency Graph has {len(vag.nodes)} vertices, {len(vag.edges)} edges"
        )
        # Test if the graph edges match with the B-rep edge orientations
        for (v1_idx, v2_idx) in vag.edges:
            self.assertTrue(vag.nodes[v1_idx]["vertex"].__hash__() == vag.edges[(v1_idx, v2_idx)]["edge"].start_vertex().__hash__())

        # Face-adjacency graph
        fag = face_adjacency(solid)
        if fag is not None:
            print(
                f"\tFace Adjacency Graph has {len(fag.nodes)} vertices, {len(fag.edges)} edges"
            )
        # Test if the graph edges match with the B-rep edge orientations
        for (f1_idx, f2_idx) in fag.edges:
            brep_face1 = fag.nodes[f1_idx]["face"]
            brep_face2 = fag.nodes[f2_idx]["face"]
            brep_edge = fag.edges[(f1_idx, f2_idx)]["edge"]
            left_face, _ = brep_edge.find_left_and_right_faces([brep_face1, brep_face2])
            self.assertTrue(brep_face1.__hash__() == left_face.__hash__())

    def run_test(self, solid):
        self.perform_tests_on_solid(solid)
