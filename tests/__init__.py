# System
import unittest

# Add the src directory to path so that occwl can be found
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# OCC
from tests.test_entity_mapper import EntityMapperTester
from tests.test_arc_length_param_finder import ArcLengthParamFinderTester
from tests.test_edge_data_extractor import EdgeDataExtractorTester
from tests.test_grid_and_normals import GridTester
from tests.test_box import BoxTester
from tests.test_edge import EdgeTester
from tests.test_face import FaceTester
from tests.test_get_triangles import TriangleTester
from tests.test_graph import GraphTester

