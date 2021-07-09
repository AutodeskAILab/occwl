from OCC.Core.TopoDS import TopoDS_Wire
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
        assert isinstance(topods_wire, TopoDS_Wire)
        super().__init__(topods_wire)
        self._wire_exp = TopologyUtils.WireExplorer(self.topods_shape())

    @deprecated(
        target=None, deprecated_in="0.01", remove_in="0.03", stream=logging.warning
    )
    def topods_wire(self):
        """
        Get the underlying OCC wire type

        Returns:
            OCC.Core.TopoDS.TopoDS_Wire: Wire
        """
        return self.topods_shape()

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
