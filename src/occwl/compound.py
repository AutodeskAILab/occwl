from OCC.Core.TopoDS import TopoDS_Compound, TopoDS_CompSolid
from OCC.Extend.DataExchange import read_step_file, list_of_shapes_to_compound
from occwl.shape import Shape
from occwl.solid import Solid
from occwl.face import Face
from occwl.wire import Wire
from occwl.edge import Edge
from occwl.vertex import Vertex


class Compound(Shape):
    """
    A compound which can be worked with as many shapes
    lumped together.
    """
    def __init__(self, shape):
        assert isinstance(shape, TopoDS_Compound)
        super().__init__(shape)
    
    @staticmethod
    def load_from_step(filename, verbosity=False):
        """
        Load everything from a STEP file as a single Compound

        Args:
            filename (str or pathlib.Path): STEP filename
            verbosity (bool): Whether to print detailed information while loading

        Returns:
            occwl.compound.Compound: Compound shape
        """
        shp = read_step_file(str(filename), as_compound=True, verbosity=False)
        if not isinstance(shp, TopoDS_Compound):
            shp, success = list_of_shapes_to_compound([shp])
            assert success
        return Compound(shp)

    def num_solids(self):
        """
        Number of solids in the Compound

        Returns:
            int: Number of faces
        """
        return self._top_exp.number_of_solids()

    def num_faces(self):
        """
        Number of faces in the Compound

        Returns:
            int: Number of faces
        """
        return self._top_exp.number_of_faces()

    def num_wires(self):
        """
        Number of wires in the Compound

        Returns:
            int: Number of wires
        """
        return self._top_exp.number_of_wires()

    def num_edges(self):
        """
        Number of edges in the Compound

        Returns:
            int: Number of edges
        """
        return self._top_exp.number_of_edges()

    def num_vertices(self):
        """
        Number of vertices in the Compound

        Returns:
            int: Number of vertices
        """
        return self._top_exp.number_of_vertices()

    def vertices(self):
        """
        Get an iterator to go over all vertices in the Compound

        Returns:
            Iterator[occwl.vertex.Vertex]: Vertex iterator
        """
        return map(Vertex, self._top_exp.vertices())

    def edges(self):
        """
        Get an iterator to go over all edges in the Compound

        Returns:
            Iterator[occwl.edge.Edge]: Edge iterator
        """
        return map(Edge, self._top_exp.edges())

    def faces(self):
        """
        Get an iterator to go over all faces in the Compound

        Returns:
            Iterator[occwl.face.Face]: Face iterator
        """
        return map(Face, self._top_exp.faces())

    def wires(self):
        """
        Get an iterator to go over all wires in the Compound

        Returns:
            Iterator[occwl.wire.Wire]: Wire iterator
        """
        return map(Wire, self._top_exp.wires())

    def solids(self):
        """
        Get an iterator to go over all solids in the Compound

        Returns:
            Iterator[occwl.solid.Solid]: Solid iterator
        """
        return map(Solid, self._top_exp.solids())
    