"""
Base class for faces, edges and vertices
"""
# OCC
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape
from OCC.Core.Extrema import Extrema_ExtFlag_MIN

# occwl
import occwl.geometry.geom_utils as geom_utils

class ClosestPointData:
    """
    A class to record information about the closest point on a shape
    to some datum point
    """

    def __init__(self, dist_shape_shape):
        """
        Args:
            dist_shape_shape (BRepExtrema_DistShapeShape): OCC class for distance to a shape
        """
        assert dist_shape_shape.IsDone()
        self.closest_entity = dist_shape_shape.SupportOnShape2(1)
        self.closest_point = geom_utils.gp_to_numpy(dist_shape_shape.PointOnShape2(1))
        self.distance = dist_shape_shape.Value()

class Shape:

    def find_closest_point_data(self, datum):
        """
        Find the information about the closest point on this shape
        
        Args:
            datum (np.ndarray): 3D Point
        
        Returns:
            ClosestPointData: Data about the closest point on this shape
            None: if error
        """
        # Folowing https://dev.opencascade.org/content/how-retrieve-nearest-face-shape-given-gppnt
        # Create a vertex from the point
        occ_point = geom_utils.numpy_to_gp(datum)
        vertex_maker = BRepBuilderAPI_MakeVertex(occ_point)
        vertex = vertex_maker.Shape()
        dist_shape_shape = BRepExtrema_DistShapeShape(
            vertex, 
            self.topods_shape(),
            Extrema_ExtFlag_MIN
        )
        ok = dist_shape_shape.Perform()
        if not ok:
            return None

        return ClosestPointData(dist_shape_shape)
