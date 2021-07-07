from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pnt2d
from OCC.Core.TopoDS import TopoDS_Vertex
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex

from occwl.geometry import geom_utils
from occwl.shape import Shape

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
        self._vertex = topods_vertex

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

    def topods_shape(self):
        """
        Get the underlying OCC vertex as a shape

        Returns:
            OCC.Core.TopoDS.TopoDS_Vertex: Vertex
        """
        return self._vertex

    def __hash__(self):
        """
        Hash for the vertex

        Returns:
            int: Hash value
        """
        return self.topods_shape().__hash__()
    
    def __eq__(self, other):
        """
        Equality check for the vertex
        """
        return self.topods_shape().__hash__() == other.topods_shape().__hash__()

    def point(self):
        """
        3D point stored in this vertex

        Returns:
            np.ndarray: 3D Point
        """
        pt = BRep_Tool.Pnt(self.topods_shape())
        return (pt.X(), pt.Y(), pt.Z())

    def topods_vertex(self):
        """
        DEPRECATED: Get the underlying OCC vertex type

        Returns:
            OCC.Core.TopoDS.TopoDS_Vertex: Vertex
        """
        return self._vertex
