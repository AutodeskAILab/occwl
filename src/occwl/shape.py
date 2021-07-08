"""
Base class for faces, edges and vertices
"""
import numpy as np
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape
from OCC.Core.Extrema import Extrema_ExtFlag_MIN
from OCC.Core.gp import gp_Ax1
from OCC.Core.TopoDS import (TopoDS_Edge, TopoDS_Face, TopoDS_Shell,
                             TopoDS_Solid, TopoDS_Vertex, TopoDS_Wire)
from OCC.Extend.ShapeFactory import (rotate_shape, rotate_shp_3_axis,
                                     scale_shape, translate_shp)

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
    def __init__(self, topods_shape):
        """
        Construct the Shape (this class is not meant to be instantiated directly)

        Args:
            topods_shape (OCC.Core.TopoDS.TopoDS_Vertex/Edge/Face/Wire/Shell/Solid): OCC TopoDS_* as provided by the derived class

        Raises:
            Exception: [description]
        """
        if type(self) == Shape:
            raise Exception("Shape must be subclassed and instantiated.")
        assert isinstance(topods_shape, (TopoDS_Vertex, TopoDS_Edge, TopoDS_Face, TopoDS_Wire, TopoDS_Shell, TopoDS_Solid))
        self._shape = topods_shape
    
    def topods_shape(self):
        """
        Get the underlying OCC shape

        Returns:
            OCC.Core.TopoDS.TopoDS_Vertex/Edge/Face/Wire/Shell/Solid: OCC TopoDS_*
        """
        return self._shape

    def __hash__(self):
        """
        Hash for the shape

        Returns:
            int: Hash value
        """
        return self.topods_shape().__hash__()
    
    def __eq__(self, other):
        """
        Equality check for the shape

        NOTE: This function only checks if the shape is the same.
        It doesn't check the edge orienation for example, so 
        
        edge1 == edge2

        does not necessarily mean 

        edge1.reversed() == edge2.reversed()
        """
        return self.topods_shape().__hash__() == other.topods_shape().__hash__()

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

    def translate(self, offset):
        """
        Translate the shape by an offset vector

        Args:
            offset (np.ndarray): Offset vector
        """
        self._shape = translate_shp(self._shape, geom_utils.numpy_to_gp_vec(offset))

    def rotate_axis_angle(self, axis, angle_radians, origin=np.zeros(3, dtype=np.float32)):
        """
        Rotate the shape about the given axis by the given angle in radians

        Args:
            axis (np.ndarray): Rotation axis
            angle_radians (float): Angle in radians
        """
        self._shape = rotate_shape(self._shape, gp_Ax1(geom_utils.numpy_to_gp(origin), geom_utils.numpy_to_gp_dir(axis)), angle_radians, unite="rad")
        
        
    def rotate_euler_angles(self, angles_xyz_radians):
        """
        Rotate the shape by the given Euler angles in radians

        Args:
            angle_xyz_radians (np.ndarray): 3D array with angles to rotate about x-axis, y-axis and z-axis respectively in radians
        """
        self._shape = rotate_shp_3_axis(self._shape, angles_xyz_radians[0], angles_xyz_radians[1], angles_xyz_radians[2], unity="rad")
    
    def scale(self, scale_vector):
        """
        Scale the shape by the given 3D vector

        Args:
            scale_vector (np.ndarray): 3D array with scales to resize the shape along the x-axis, y-axis and z-axis respectively
        """
        self._shape = scale_shape(self._shape, scale_vector[0], scale_vector[1], scale_vector[2])
