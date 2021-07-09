"""
Tools for finding an arc-length parameterization from an edge,
curve interval or surface iso-parametric curve
"""
import numpy as np

# occwl
from occwl.geometry.interval import Interval


class ArcLengthParamFinder:
    def __init__(self, points=None, us=None, edge=None, num_arc_length_samples=100):
        """
        Create a class to generate arc-length parameters

        Args:
            points (list(np.array)): Point samples on the curve
            us (list(float)): u parameters on the curve

            or

            edge (occwl.edge.Edge): An edge
            num_arc_length_samples (int): The number of samples to use the the calculation
        """
        self.good = True
        if edge is not None:
            # For an edge we can sample points directly
            self._generate_data_from_edge(edge, num_arc_length_samples)
        else:
            # This code could be expanded to sample from surface iso-parametric lines
            assert points is not None
            assert us is not None
            self.points = points
            self.us = us

    def find_arc_length_parameters(self, num_samples):
        """
        Find a list of u parameters which provides an equal arc length
        list for the given points and us
        """
        assert num_samples >= 2
        assert len(self.points) >= 2
        assert len(self.us) == len(self.points)

        # Find the arc lengths between the sample points
        lengths = []
        total_length = 0
        prev_point = None
        for point in self.points:
            if prev_point is not None:
                length = np.linalg.norm(point - prev_point)
                lengths.append(length)
                total_length += length
            prev_point = point

        # Find the cumulative arc length over the points
        arc_length_fraction = [0.0]
        cumulative_length = 0.0
        for length in lengths:
            cumulative_length += length
            arc_length_fraction.append(cumulative_length / total_length)

        # Build the arc-length parameterization
        arc_length_params = []
        arc_length_index = 0
        for i in range(num_samples):
            desired_arc_length_fraction = i / (num_samples - 1)

            # Find the correct span of the polyline
            while arc_length_fraction[arc_length_index] < desired_arc_length_fraction:
                arc_length_index += 1
                if arc_length_index >= len(arc_length_fraction) - 1:
                    break

            # Handle the special case at the first point
            if arc_length_index == 0:
                u_low = self.us[0]
                frac_low = arc_length_fraction[0]
            else:
                u_low = self.us[arc_length_index - 1]
                frac_low = arc_length_fraction[arc_length_index - 1]

            # Find the arc length parameter by interpolation
            u_high = self.us[arc_length_index]
            frac_high = arc_length_fraction[arc_length_index]

            # Check we found the correct range
            assert desired_arc_length_fraction >= frac_low
            assert desired_arc_length_fraction <= frac_high

            d_frac = frac_high - frac_low
            if d_frac <= 0.0:
                u_param = u_low
            else:
                u_interval = Interval(u_low, u_high)
                position_in_interval = (desired_arc_length_fraction - frac_low) / (
                    d_frac
                )
                u_param = u_interval.interpolate(position_in_interval)
            arc_length_params.append(u_param)

        return arc_length_params

    def _generate_data_from_edge(self, edge, num_points_arclength):
        interval = edge.u_bounds()
        if interval.invalid():
            self.good = False
            return
        self.points = []
        self.us = []
        for i in range(num_points_arclength):
            u = interval.interpolate(i / (num_points_arclength - 1))
            self.points.append(edge.point(u))
            self.us.append(u)

    def _check_non_decreasing(self, us):
        prev = us[0]
        for u in us:
            if u < prev:
                return False
            prev = u
        return True
