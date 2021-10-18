from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pnt2d
from OCC.Core.TopoDS import TopoDS_Vertex
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
import logging

from occwl.geometry import geom_utils
from occwl.shape import Shape
from deprecate import deprecated


class Vertex(Shape):
    """
    A topological vertex in a solid model
    Represents a 3D geometric point
    """

    def __init__(self, topods_vertex):
        """
        Constructor to initialize a vertex from a TodoDS_Vertex

        Args:
            topods_vertex (OCC.Core.TopoDS.TopoDS_Vertex): OCC Vertex
        """
        assert isinstance(topods_vertex, TopoDS_Vertex)
        super().__init__(topods_vertex)

    @staticmethod
    def make_vertex(point):
        """
        Create a vertex from a 3D point
        
        Args:
            point (np.ndarray): 3D Point
        
        Returns:
            occwl.Vertex: Vertex representing the 3D point
        """
        occ_point = geom_utils.numpy_to_gp(point)
        vertex_maker = BRepBuilderAPI_MakeVertex(occ_point)
        vertex = vertex_maker.Shape()
        return Vertex(vertex)

    def point(self):
        """
        3D point stored in this vertex

        Returns:
            np.ndarray: 3D Point
        """
        pt = BRep_Tool.Pnt(self.topods_shape())
        return geom_utils.gp_to_numpy(pt)


