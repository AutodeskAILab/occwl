from OCC.Core.ShapeAnalysis import ShapeAnalysis_Wire


class Wire:
    """
    A topological wire in a solid model
    Represents a closed loop of edges
    """
    def __init__(self, topods_wire):
        assert isinstance(topods_wire, TopoDS_Wire)
        self._wire = topods_wire
        self._wire_exp = None
    
    def topods_wire(self):
        """
        Get the underlying OCC wire type

        Returns:
            OCC.Core.TopoDS.TopoDS_Wire: Wire
        """
        return self._wire

    def hash(self):
        """
        Hash for the wire

        Returns:
            int: Hash value
        """
        return hash(self.topods_wire())

    def ordered_edges(self):
        pass

    def ordered_vertices(self):
        pass
