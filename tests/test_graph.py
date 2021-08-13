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
        vag = vertex_adjacency(solid)
        print(
            f"\tVertex Adjacency Graph has {len(vag.nodes)} vertices, {len(vag.edges)} edges"
        )
        fag = face_adjacency(solid, self_loops=True)
        if fag is not None:
            print(
                f"\tFace Adjacency Graph has {len(fag.nodes)} vertices, {len(fag.edges)} edges"
            )

    def run_test(self, solid):
        self.perform_tests_on_solid(solid)
