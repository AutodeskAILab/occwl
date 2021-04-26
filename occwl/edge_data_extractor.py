"""
Extract points, normals and potentially other information from an edge and its
adjacent faces
"""

from enum import Enum

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
            EdgeDataExtractor.normals1
            EdgeDataExtractor.normals2

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

        self.edge = edge
        self.face1 = face1
        self.surf1 = BRepAdaptor_Surface(face1.topods_face())
        self.face2 = face2
        self.surf2 = BRepAdaptor_Surface(face2.topods_face())

        self.curve3d = edge.curve()
        self.pcurve1 = BRepAdaptor_Curve2d(edge.topods_edge(), self.surf1)
        self.pcurve2 = BRepAdaptor_Curve2d(edge.topods_edge(), self.surf2)

        # Find the parameters to evaluate.   These will be
        # ordered based on the reverse flag of the edge
        self.u_params = self.find_arclength_parameters()
        self.surf1_uvs = self.find_uvs(self.pcurve1)
        self.surf2_uvs = self.find_uvs(self.pcurve2)

        # Find 3d points and tangents.
        # These will be ordered and oriented based on the 
        # direction of the edge.  i.e. we will apply the reverse
        # flag
        self.points = self.evaluate_3d_points()
        self.tangents = self.evaluate_curve_tangents()

        # Test here on watertight models to make sure
        # that the uvs we found are parameterized in the
        # same way as the 3d curve
        self.sanity_check_uvs(self.surf1_uvs, edge.tolerance())
        self.sanity_check_uvs(self.surf2_uvs, edge.tolerance())

        # Generate the normals.  These will be ordered
        # based on the direction of the edge and the 
        # normals will be reversed based on the orientation
        # of the faces
        self.normals1 = self.evaluate_surface_normals(self.face1)
        self.normals2 = self.evaluate_surface_normals(self.face2)


    def edge_convexity(self, angle_tol_rads):
        """
        Compute the convexity of the edge
        """
        continuity = BRep_Tool_Continuity(
            self.edge.topods_edge(), 
            self.face1.topods_face(),
            self.face2.topods_face()
        )
        is_smooth = self.check_smooth(angle_tol_rads)
        if is_smooth:
            return EdgeConvexity.SMOOTH

        cross_prod_of_normals = np.linalg.cross(self.normals1, self.normals2, axis=0)
        dot_product_with_tangents = np.linalg.dot(cross_prod_of_normals, self.tangents, axis=0)

        if dot_product_with_tangents.sum() > 0.0:
            return EdgeConvexity.CONVEX
        returnEdgeConvexity.CONCAVE


    def find_arclength_parameters(self):
        num_points_arclength = 100
        interval = self.edge.u_bound()
        points = []
        us = []
        for i in range(num_samples):
            u = interval.interpolate(i/(num_points_arclength-1)
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
                toltal_length += length
            prev_point = point

        arc_length_fraction = [ 0.0 ]
        for length in lengths:
            arc_length_fraction.append(length/total_length)

        arc_length_params = []
        arc_length_index = 0
        for i in range(self.num_samples):
            desired_arc_length_fraction = i/(self.num_samples-1)
            while arc_length_fraction[arc_length_index] < desired_arc_length_fraction:
                arc_length_index += 1
                if arc_length_index == len(arc_length_fraction)-1
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
            assert d_frac > 0.0
            u_interval = Interval(low, high)
            position_in_interval = (desired_arc_length_fraction-frac_low)/(d_frac)
            u_param = u_interval.interpolate(position_in_interval)
            arc_length_params.append(u_param)

        # Now we need to check the orientation of the edge and 
        # reverse the array is necessary
        if self.edge.reversed():
            reversed_arc_length_params = []
            for param in arc_length_params.reversed():
                reversed_arc_length_params.append(param)
            return reversed_arc_length_params

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
        for u, uv1, uv2 in zip(self.u_params, self.surf1_uvs, self.surf2_uvs):
            point = self.edge.point(u)
            point1 = self.face1.point(uv1)
            point2 = self.face1.point(uv2)
            assert np.linalg.norm(point-point1) < edge_tolerance
            assert np.linalg.norm(point-point2) < edge_tolerance

    def evaluate_surface_normals(self, uvs, face):
        normals = []
        for uv in uvs:
            normal = face.normal(uv)
            normals.append(normal)
        return np.stack(normalsal)