"""
Base class for faces, edges and vertices
"""

class ClosestPointData:
    """
    A class to record information about the closest point on a shape
    to some datum point
    """

    def __init__(
        closest_entity,  # The closest sub-shape to the point
        closest_point,   # The closest point on the shape
        distance         # The distance to the closest point
    ):
    self.closest_entity = closest_entity
    self.closest_point = closest_point
    self.distance = distance

class Shape:

    def find_closest_point_data(datum):
        """
        Find the information about the closest point on this shape
        """