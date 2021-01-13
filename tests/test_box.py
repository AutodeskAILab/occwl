# System
from pathlib import Path
import numpy as np

# OCC
from geometry.box import Box
from geometry.interval import Interval

# Test
from test_base import TestBase

class BoxTester(TestBase):

    def test_encompass(self):
        # 2D point
        pt2d = np.array([0.5, 1])
        box2d = Box(pt2d)
        self.assertTrue(np.array_equal(box2d.min_point(), pt2d))
        self.assertTrue(np.array_equal(box2d.max_point(), pt2d))

        # Another 2d point
        pt2d2 = np.array([-1.0, 1])
        box2d.encompass_point(pt2d2)
        self.assertTrue(np.array_equal(box2d.min_point(), np.array([-1, 1])))
        self.assertTrue(np.array_equal(box2d.max_point(), np.array([0.5, 1])))

        another_box2d = Box()
        another_box2d.encompass_box(box2d)

        pt2d3 = np.array([5, 5])
        box2d.encompass_point(pt2d3)
        another_box2d.encompass_box(box2d)
        self.assertTrue(np.array_equal(box2d.min_point(), np.array([-1, 1])))
        self.assertTrue(np.array_equal(box2d.max_point(), np.array([5, 5])))
        self.assertTrue(box2d.contains_point(np.array([0,1])))
        self.assertTrue(another_box2d.contains_box(box2d))

    def test_center(self):
        pt1 = np.array([1,2,3])
        pt2 = np.array([2,3,4])
        box = Box()
        box.encompass_point(pt1)
        box.encompass_point(pt2)
        c = box.center()
        self.assertTrue(np.array_equal(c, np.array([1.5, 2.5, 3.5])))


    def test_box(self):
        pt1 = np.array([0,0,0])
        pt2 = np.array([2,3,4])
        box = Box()
        box.encompass_point(pt1)
        box.encompass_point(pt2)
        d = box.diagonal()
        self.assertTrue(np.array_equal(d,np.array([2, 3, 4])))
        box.offset(1)
        self.assertTrue(np.array_equal(box.min_point(), np.array([-1, -1, -1])))
        self.assertTrue(np.array_equal(box.max_point(), np.array([3,4,5])))

    def test_interpolate(self):
        interval = Interval(1,2)
        self.assertEqual(interval.interpolate(0.25), 1.25)
        self.assertEqual(interval.interpolate(0.75), 1.75)