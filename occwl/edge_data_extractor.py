"""
Extract points, normals and potentially other information from an edge and its
adjacent faces
"""
# System
from enum import Enum
import numpy as np

# OCC
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve2d, BRepAdaptor_Surface
from OCC.Core.gp import gp_Pnt2d

# occwl
from occwl.geometry.interval import Interval

class EdgeConvexity(Enum):
    CONCAVE = 1
    CONVEX = 2
    SMOOTH = 3

class EdgeDataExtractor:
    def __init__(self, edge, face1, face2, num_samples):
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
        EdgeDataExtractor.false and all arrays get set to 
        zero vectors
        """
        assert num_samples > 0
        assert edge is not None
        assert face1 is not None
        assert face2 is not None

        self.num_samples = num_samples
        self.good = True

        self.find_left_and_right_faces(edge, face1, face2)

        self.edge = edge
        # self.left_surf = BRepAdaptor_Surface(self.left_face.topods_face())
        # self.right_surf = BRepAdaptor_Surface(self.right_face.topods_face())

        self.curve3d = edge.curve()
        self.left_pcurve = BRepAdaptor_Curve2d(edge.topods_edge(), self.left_face.topods_face())
        self.right_pcurve = BRepAdaptor_Curve2d(edge.topods_edge(), self.right_face.topods_face())

        # Find the parameters to evaluate.   These will be
        # ordered based on the reverse flag of the edge
        self.u_params = self.find_arclength_parameters()
        if not self.good:
            return
        self.left_uvs = self.find_uvs(self.left_pcurve)
        self.right_uvs = self.find_uvs(self.right_pcurve)

        # Find 3d points and tangents.
        # These will be ordered and oriented based on the 
        # direction of the edge.  i.e. we will apply the reverse
        # flag
        self.points = self.evaluate_3d_points()
        self.tangents = self.evaluate_curve_tangents()

        # Generate the normals.  These will be ordered
        # based on the direction of the edge and the 
        # normals will be reversed based on the orientation
        # of the faces
        self.left_normals = self.evaluate_surface_normals(self.left_uvs, self.left_face)
        self.right_normals = self.evaluate_surface_normals(self.right_uvs, self.right_face)

    def find_left_and_right_faces(self, edge, face1, face2):
        """
        We know two faces on either side of the edge, but we
        don't know which is to the left and which to the right.
        This function works it out
        """
        if face1.is_left_of(edge):
            # In some cases (like a cylinder) the left and right faces
            # of the edge are the same face
            if face1 != face2:
                assert not face2.is_left_of(edge)
            self.left_face = face1
            self.right_face = face2
        else:
            assert face2.is_left_of(edge)
            self.left_face = face2
            self.right_face = face1

    def edge_convexity(self, angle_tol_rads):
        """
        Compute the convexity of the edge
        """
        assert self.good
        continuity = self.edge.continuity(self.left_face, self.right_face)
        is_smooth = self.check_smooth(angle_tol_rads)
        if is_smooth:
            return EdgeConvexity.SMOOTH

        cross_prod_of_normals = np.cross(self.left_normals, self.right_normals, axis=1)
        dot_product_with_tangents = np.multiply(cross_prod_of_normals, self.tangents).sum(1)

        if dot_product_with_tangents.sum() > 0.0:
            return EdgeConvexity.CONVEX
        return EdgeConvexity.CONCAVE

    def check_smooth(self, angle_tol_rads):
        dot_prod = np.multiply(self.left_normals, self.right_normals).sum(1)
        average_dot_product = dot_prod.mean()
        return average_dot_product > np.cos(angle_tol_rads)

    def find_arclength_parameters(self):
        num_points_arclength = 100
        interval = self.edge.u_bounds()
        if interval.invalid():
            self.good = False
            return
        points = []
        us = []
        for i in range(num_points_arclength):
            u = interval.interpolate(i/(num_points_arclength-1))
            points.append(self.edge.point(u))
            us.append(u)

        # Find the arc lengths between the sample points
        lengths = []
        total_length = 0
        prev_point = None
        for point in points:
            if prev_point is not None:
                length = np.linalg.norm(point-prev_point)
                lengths.append(length)
                total_length += length
            prev_point = point

        arc_length_fraction = [ 0.0 ]
        cumulative_length = 0.0
        for length in lengths:
            cumulative_length += length
            arc_length_fraction.append(cumulative_length/total_length)
            

        arc_length_params = []
        arc_length_index = 0
        for i in range(self.num_samples):
            desired_arc_length_fraction = i/(self.num_samples-1)
            while arc_length_fraction[arc_length_index] < desired_arc_length_fraction:
                arc_length_index += 1
                if arc_length_index >= len(arc_length_fraction)-1:
                    break

            if arc_length_index == 0:
                u_low = us[0]
                frac_low = arc_length_fraction[0]
            else:
                u_low = us[arc_length_index-1]
                frac_low = arc_length_fraction[arc_length_index-1]
            u_high = us[arc_length_index]
            frac_high = arc_length_fraction[arc_length_index]
            d_frac = frac_high-frac_low
            if d_frac <= 0.0:
                u_param = u_low
            else:
                u_interval = Interval(u_low, u_high)
                position_in_interval = (desired_arc_length_fraction-frac_low)/(d_frac)
                u_param = u_interval.interpolate(position_in_interval)
            arc_length_params.append(u_param)

        # Now we need to check the orientation of the edge and 
        # reverse the array is necessary
        if self.edge.reversed():
            arc_length_params.reverse()
        return arc_length_params


    def find_uvs(self, pcurve):
        uvs = []
        for u in self.u_params:
            uv = gp_Pnt2d()
            pcurve.D0(u, uv)
            uv = np.array([uv.X(), uv.Y()])
            uvs.append(uv)
        return uvs

    def evaluate_3d_points(self):
        points = []
        for u in self.u_params:
            point = self.edge.point(u)
            points.append(point)
        return np.stack(points)


    def evaluate_curve_tangents(self):
        tangents = []
        for u in self.u_params:
            tangent = self.edge.tangent(u)
            tangents.append(tangent)
        return np.stack(tangents)

    def sanity_check_uvs(self, uvs, edge_tolerance):
        for u, left_uv, right_uv in zip(self.u_params, self.left_uvs, self.right_uvs):
            point = self.edge.point(u)
            point1 = self.left_face.point(left_uv)
            point2 = self.right_face.point(right_uv)
            assert np.linalg.norm(point-point1) < edge_tolerance
            assert np.linalg.norm(point-point2) < edge_tolerance

    def evaluate_surface_normals(self, uvs, face):
        normals = []
        for uv in uvs:
            normal = face.normal(uv)
            normals.append(normal)
        return np.stack(normals)