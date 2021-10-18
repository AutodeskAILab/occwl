from OCC.Core.TopoDS import TopoDS_Wire
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeWire
from OCC.Extend import TopologyUtils
from occwl.edge import Edge
from occwl.vertex import Vertex

from occwl.shape import Shape
from deprecate import deprecated
import logging


class Wire(Shape):
    """
    A topological wire in a solid model
    Represents a closed loop of edges
    """

    def __init__(self, topods_wire):
        """
        Construct a Wire

        Args:
            topods_wire (OCC.Core.TopoDS_Wire): OCC wire type
        """
        assert isinstance(topods_wire, TopoDS_Wire)
        super().__init__(topods_wire)
        self._wire_exp = TopologyUtils.WireExplorer(self.topods_shape())

    @staticmethod
    def make_from_edges(edges):
        """
        Make a wire from connected edges

        Args:
            edges (List[occwl.edge.Edge]): List of edges

        Returns:
            occwl.wire.Wire or None: Returns a Wire or None if the operation failed
        """
        wire_builder = BRepBuilderAPI_MakeWire()
        for edge in edges:
            wire_builder.Add(edge.topods_shape())
        wire_builder.Build()
        if not wire_builder.IsDone():
            return None
        return Wire(wire_builder.Wire())

    def ordered_edges(self):
        """
        Get an iterator to go over the edges while respecting the wire ordering

        Returns:
            Iterator[occwl.edge.Edge]: An iterator to edges
        """
        return map(Edge, self._wire_exp.ordered_edges())

    def ordered_vertices(self):
        """
        Get an iterator to go over the vertices while respecting the wire ordering

        Returns:
            Iterator[occwl.vertex.Vertex]: An iterator to vertices
        """
        return map(Vertex, self._wire_exp.ordered_vertices())
