# System
import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# OCC
from test_grid_and_normals import GridTester

if __name__ == '__main__':
    unittest.main()