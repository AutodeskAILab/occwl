
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
from test_base import TestBase


class GraphTester(TestBase):

    def test_solid(self):
        data_folder = self.test_folder() / "test_data"
        self.run_test_on_all_files_in_folder(data_folder)

    def perform_tests_on_solid(self, solid):
        brep_vertices, brep_edges, vag_edges = vertex_adjacency(solid)
        print(f"\tVertex Adjacency Graph has {len(brep_vertices)} vertices, {len(vag_edges)} edges")
        brep_faces, brep_dual_edges, fag_edges = face_adjacency(solid)
        print(f"\tFace Adjacency Graph has {len(brep_faces)} vertices, {len(fag_edges)} edges")

    def run_test(self, solid):
        self.perform_tests_on_solid(solid)

