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

# PythonOCC
from OCC.Extend.TopologyUtils import TopologyExplorer, WireExplorer

    

class EntityMapper:
    """
    This class allows us to map between occwl entities and integer
    identifiers which can be used as indices into arrays of feature vectors
    or the rows and columns of incidence matrices. 
    """
    def __init__(self, solids):
        """
        Create a mapper object for this list of solids

        Args:
            solids (list(occwl.solid.Solid)): An array of solids
            or
            solids (occwl.solid.Solid): A single solid
        """

        # Create the dictionaries which will map the
        # objects hash values to the indices.
        self.solid_map = dict()
        self.face_map = dict()
        self.wire_map = dict()
        self.edge_map = dict()
        self.oriented_edge_map = dict()
        self.vertex_map = dict()

        
        # Create list if only one solid is passed in
        if isinstance(solids, occwl.solid.Solid): 
            solids = [solids]

        for solid in solids:
    
            # Build the index lookup tables
            self.append_solid(solid)
            self.append_faces(solid)
            self.append_wires(solid)
            self.append_edges(solid)
            self.append_oriented_edges(solid)
            self.append_vertices(solid)


    # The following functions are the interface for 
    # users of the class to access the indices
    # which will reptresent the Open Cascade entities
    
    def get_num_edges(self):
        return len(self.edge_map.keys())

    def get_num_faces(self):
        return len(self.face_map.keys())

    def solid_index(self, solid):
        """
        Find the index of a solid
        """
        h = self.get_hash(solid)
        return self.solid_map[h]

    def face_index(self, face):
        """
        Find the index of a face
        """
        h = self.get_hash(face)
        return self.face_map[h]

    def wire_index(self, wire):
        """
        Find the index of a wire
        """
        h = self.get_hash(wire)
        return self.wire_map[h]

    def edge_index(self, edge):
        """
        Find the index of an edge
        """
        h = self.get_hash(edge)
        return self.edge_map[h]
    
    def oriented_edge_index(self, oriented_edge):
        """
        Find the index of a oriented edge.  i.e. a coedge
        """
        h = self.get_hash(oriented_edge)
        is_reversed = oriented_edge.reversed()
        tup = (h,is_reversed)
        return self.oriented_edge_map[tup]

    def oriented_edge_exists(self, oriented_edge):
        h = self.get_hash(oriented_edge)
        is_reversed = oriented_edge.reversed()
        tup = (h,orientation)
        return tup in self.oriented_edge_map

    def vertex_index(self, vertex):
        """
        Find the index of a vertex
        """
        h = self.get_hash(vertex)
        return self.vertex_map[h]



    # These functions are used internally to build the map

    def get_hash(self, ent):
        return ent.__hash__()

    def append_solid(self, solid):
        h = self.get_hash(solid)
        index = len(self.solid_map)
        assert not h in self.solid_map
        self.solid_map[h] = index

    def append_solid(self, solid):
        h = self.get_hash(solid)
        index = len(self.solid_map)
        assert not h in self.solid_map
        self.solid_map[h] = index

    def append_faces(self, solid):
        faces = solid.faces()
        for face in faces:
            self.append_face(face)

    def append_face(self, face):
        h = self.get_hash(face)
        index = len(self.face_map)
        assert not h in self.face_map
        self.face_map[h] = index

    def append_wire(self, solid):
        wires = solid.wires()
        for wire in wires:
            self.append_wire(wire)

    def append_wire(self, wire):
        h = self.get_hash(wire)
        index = len(self.wire_map)
        assert not h in self.wire_map
        self.wire_map[h] = index

    def append_edges(self, solid):
        edges = solid.edges()
        for edge in edges:
            self.append_edge(edge)

    def append_edge(self, edge):
        h = self.get_hash(edge)
        index = len(self.edge_map)
        assert not h in self.edge_map
        self.edge_map[h] = index

    def append_oriented_edges(self, solid):
        wires = solid.wires()
        for wire in wires:
            oriented_edges = wire.ordered_edges()
            for oriented_edge in oriented_edges:
                self.append_oriented_edge(oriented_edge)

    def append_oriented_edge(self, oriented_edge):
        h = self.get_hash(oriented_edge)
        is_reversed = oriented_edge.reversed()
        tup = (h,is_reversed)
        index = len(self.halfedge_map)
        if not tup in self.halfedge_map:
            self.halfedge_map[tup] = index

    def append_vertices(self, solid):
        vertices = solid.vertices()
        for vertex in vertices:
            self.append_vertex(vertex)

    def append_vertex(self, vertex):
        h = self.get_hash(vertex)
        index = len(self.vertex_map)
        assert not h in self.vertex_map
        self.vertex_map[h] = index
