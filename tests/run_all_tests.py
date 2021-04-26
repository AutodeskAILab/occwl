# System
import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# OCC
from test_grid_and_normals import GridTester
from test_box import BoxTester
from test_edge import EdgeTester
from test_face import FaceTester
from test_get_triangles import TriangleTester
from test_graph import GraphTester

if __name__ == '__main__':
    unittest.main()