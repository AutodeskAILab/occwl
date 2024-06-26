"""
A class to extract points and normals from the two faces adjacent to an edge.
This can then be used to compute the edges convexity.
"""
# System
from enum import Enum
import numpy as np

# OCC
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve2d, BRepAdaptor_Surface
from OCC.Core.gp import gp_Pnt2d, gp_Identity

# occwl
from occwl.geometry.interval import Interval
from occwl.geometry.arc_length_param_finder import ArcLengthParamFinder
import occwl.geometry.geom_utils as geom_utils 

class EdgeConvexity(Enum):
    CONCAVE = 1
    CONVEX = 2
    SMOOTH = 3


class EdgeDataExtractor:
    def __init__(self, edge, faces, num_samples=10, use_arclength_params=True):
        """
        Compute point and normal data for an oriented edge of the model.
        The arrays of points, tangents and normals are all oriented based
        on the orientation flag of the edge.

        You can access the data from the member numpy arrays

            EdgeDataExtractor.points
            EdgeDataExtractor.tangests
            EdgeDataExtractor.left_normals
            EdgeDataExtractor.right_normals

        If a problem was detected during the calculation then 
        EdgeDataExtractor.good == false
        """
        assert num_samples > 0, "num_samples must be bigger than 0"
        assert edge is not None
        assert len(faces) > 0, "Expect 1 or 2 faces adjacent to an edge"

        self.num_samples = num_samples
        self.good = True
        self.left_face, self.right_face = edge.find_left_and_right_faces(faces)
        if self.left_face is None or self.right_face is None:
            # Cope with case where the left and right face cannot be found
            self.good = False
            return

        self.edge = edge
        self.curve3d = edge.curve()
        self.left_pcurve = BRepAdaptor_Curve2d(
            edge.topods_shape(), self.left_face.topods_shape()
        )
        self.right_pcurve = BRepAdaptor_Curve2d(
            edge.topods_shape(), self.right_face.topods_shape()
        )

        # Find the parameters to evaluate.   These will be
        # ordered based on the reverse flag of the edge
        if use_arclength_params:
            self.u_params = self._find_arclength_parameters()
        else:
            self.u_params = self._find_uniform_parameters()
        if not self.good:
            return
        self.left_uvs = self._find_uvs(self.left_pcurve)
        self.right_uvs = self._find_uvs(self.right_pcurve)

        # Find 3d points and tangents.
        # These will be ordered and oriented based on the
        # direction of the edge.  i.e. we will apply the reverse
        # flag
        self.points = self._evaluate_3d_points()
        self.tangents = self._evaluate_curve_tangents()

        # Generate the normals.  These will be ordered
        # based on the direction of the edge and the
        # normals will be reversed based on the orientation
        # of the faces
        self.left_normals = self._evaluate_surface_normals(
            self.left_uvs, self.left_face
        )
        self.right_normals = self._evaluate_surface_normals(
            self.right_uvs, self.right_face
        )

    def edge_convexity(self, angle_tol_rads):
        """
        Compute the convexity of the edge
        """
        assert self.good
        is_smooth = self._check_smooth(angle_tol_rads)
        if is_smooth:
            return EdgeConvexity.SMOOTH

        cross_prod_of_normals = np.cross(self.left_normals, self.right_normals, axis=1)
        dot_product_with_tangents = np.multiply(
            cross_prod_of_normals, self.tangents
        ).sum(1)

        if dot_product_with_tangents.sum() > 0.0:
            return EdgeConvexity.CONVEX
        return EdgeConvexity.CONCAVE

    def sanity_check_uvs(self, uvs, edge_tolerance):
        """
        Assert that the points we get by evaluating uvs on both sides of the edge 
        are within the specified tolerance.

        This function is intended for testing/debugging
        """
        for u, left_uv, right_uv in zip(self.u_params, self.left_uvs, self.right_uvs):
            point = self.edge.point(u)
            point1 = self.left_face.point(left_uv)
            point2 = self.right_face.point(right_uv)
            assert np.linalg.norm(point - point1) < edge_tolerance
            assert np.linalg.norm(point - point2) < edge_tolerance

    """
    Private member functions
    """

    def _check_smooth(self, angle_tol_rads):
        dot_prod = np.multiply(self.left_normals, self.right_normals).sum(1)
        average_dot_product = dot_prod.mean()
        return average_dot_product > np.cos(angle_tol_rads)

    def _find_uniform_parameters(self):
        interval = self.edge.u_bounds()
        if interval.invalid():
            self.good = False
            return
        params = []
        for i in range(self.num_samples):
            t = i / (self.num_samples - 1)
            params.append(interval.interpolate(t))
        # Now we need to check the orientation of the edge and
        # reverse the array is necessary
        if self.edge.reversed():
            params.reverse()
        return params

    def _find_arclength_parameters(self):
        arc_length_finder = ArcLengthParamFinder(edge=self.edge)
        if not arc_length_finder.good:
            self.good = False
            return
        arc_length_params = arc_length_finder.find_arc_length_parameters(
            self.num_samples
        )
        # Now we need to check the orientation of the edge and
        # reverse the array is necessary
        if self.edge.reversed():
            arc_length_params.reverse()
        return arc_length_params

    def _find_uvs(self, pcurve):
        uvs = []
        for u in self.u_params:
            uv = gp_Pnt2d()
            pcurve.D0(u, uv)
            uv = np.array([uv.X(), uv.Y()])
            uvs.append(uv)
        return uvs

    def _evaluate_3d_points(self):
        points = []
        for u in self.u_params:
            point = self.edge.point(u)
            points.append(point)
        return np.stack(points)

    def _evaluate_curve_tangents(self):
        tangents = []
        for u in self.u_params:
            tangent = self.edge.tangent(u)
            tangents.append(tangent)
        return np.stack(tangents)

    def _evaluate_surface_normals(self, uvs, face):
        normals = []
        for uv in uvs:
            normal = face.normal(uv)
            normals.append(normal)
        return np.stack(normals)
