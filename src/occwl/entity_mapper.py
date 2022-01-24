"""
The entity mapper allows you to map between occwl entities and integer
identifiers which can be used as indices into arrays of feature vectors
or the rows and columns of incidence matrices. 

NOTE:  

    Only oriented edges which are used by wires are included in the oriented 
    edge map.  In the case of edges which are open (i.e. they are adjacent
    to a hole in the solid), only one oriented edge is present. Use the function

    EntityMapper.oriented_edge_exists(oriented_edge)

    to check if an oriented edge is used by a wire and known to the entity mapper.    
"""


class EntityMapper:
    """
    This class allows us to map between occwl entities and integer
    identifiers which can be used as indices into arrays of feature vectors
    or the rows and columns of incidence matrices. 
    """

    def __init__(self, solid):
        """
        Create a mapper object for solid

        Args:

            solid (occwl.solid.Solid): A single solid
        """

        # Create the dictionaries which will map the
        # objects hash values to the indices.
        self.face_map = dict()
        self.wire_map = dict()
        self.edge_map = dict()
        self.oriented_edge_map = dict()
        self.vertex_map = dict()

        # Build the index lookup tables
        self._append_faces(solid)
        self._append_wires(solid)
        self._append_edges(solid)
        self._append_oriented_edges(solid)
        self._append_vertices(solid)

    # The following functions are the interface for
    # users of the class to access the indices
    # which will reptresent the Open Cascade entities

    def get_num_edges(self):
        return len(self.edge_map.keys())

    def get_num_faces(self):
        return len(self.face_map.keys())

    def face_index(self, face):
        """
        Find the index of a face
        """
        h = self._get_hash(face)
        return self.face_map[h]

    def wire_index(self, wire):
        """
        Find the index of a wire
        """
        h = self._get_hash(wire)
        return self.wire_map[h]

    def edge_index(self, edge):
        """
        Find the index of an edge
        """
        h = self._get_hash(edge)
        return self.edge_map[h]

    def oriented_edge_index(self, oriented_edge):
        """
        Find the index of a oriented edge.  i.e. a coedge
        """
        h = self._get_hash(oriented_edge)
        is_reversed = oriented_edge.reversed()
        tup = (h, is_reversed)
        return self.oriented_edge_map[tup]

    def oriented_edge_exists(self, oriented_edge):
        h = self._get_hash(oriented_edge)
        is_reversed = oriented_edge.reversed()
        tup = (h, is_reversed)
        return tup in self.oriented_edge_map

    def vertex_index(self, vertex):
        """
        Find the index of a vertex
        """
        h = self._get_hash(vertex)
        return self.vertex_map[h]

    # These functions are used internally to build the map

    def _get_hash(self, ent):
        return ent.__hash__()

    def _append_faces(self, solid):
        faces = solid.faces()
        for face in faces:
            self._append_face(face)

    def _append_face(self, face):
        h = self._get_hash(face)
        index = len(self.face_map)
        assert not h in self.face_map
        self.face_map[h] = index

    def _append_wires(self, solid):
        wires = solid.wires()
        for wire in wires:
            self._append_wire(wire)

    def _append_wire(self, wire):
        h = self._get_hash(wire)
        index = len(self.wire_map)
        assert not h in self.wire_map
        self.wire_map[h] = index

    def _append_edges(self, solid):
        edges = solid.edges()
        for edge in edges:
            self._append_edge(edge)

    def _append_edge(self, edge):
        h = self._get_hash(edge)
        index = len(self.edge_map)
        assert not h in self.edge_map
        self.edge_map[h] = index

    def _append_oriented_edges(self, solid):
        wires = solid.wires()
        for wire in wires:
            oriented_edges = wire.ordered_edges()
            for oriented_edge in oriented_edges:
                self._append_oriented_edge(oriented_edge)

    def _append_oriented_edge(self, oriented_edge):
        h = self._get_hash(oriented_edge)
        is_reversed = oriented_edge.reversed()
        tup = (h, is_reversed)
        index = len(self.oriented_edge_map)
        if tup in self.oriented_edge_map:
            print("Warning! - The same oriented edge appears twice in the same solid")
        if not tup in self.oriented_edge_map:
            self.oriented_edge_map[tup] = index

    def _append_vertices(self, solid):
        vertices = solid.vertices()
        for vertex in vertices:
            self._append_vertex(vertex)

    def _append_vertex(self, vertex):
        h = self._get_hash(vertex)
        index = len(self.vertex_map)
        assert not h in self.vertex_map
        self.vertex_map[h] = index
