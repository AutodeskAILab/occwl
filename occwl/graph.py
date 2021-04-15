from occwl.solid import Solid
from occwl.face import Face
from occwl.edge import Edge
#from occwl.vertex import Vertex
import itertools


def face_adjacency(solid, self_loops=False):
    """ 
    Creates a face adjacency graph from the given solid
    :param solid: A B-rep solid model of type occwl.Solid
    :param self_loops: Whether to add self loops in the graph (default: False)
    :return: list of faces (occwl.Face), dict of edges (occwl.Edge), and a list of face index pairs for each edge in the graph.
             The indices in the connectivity index into the face list and can be used as keys in the edge dict. 
    """
    assert isinstance(solid, Solid)
    face2ind = {}
    edge2ind = {}
    nodes = []
    edges = {}
    connectivity = []
    for i, face in enumerate(solid.faces()):
        face2ind[face.hash()] = i
        nodes.append(face)

    for ei in solid.edges():
        connected_faces = list(solid.faces_from_edge(ei))
        for (fi, fj) in itertools.permutations(connected_faces):
            ind1 = face2ind[fi.hash()]
            ind2 = face2ind[fj.hash()]
            if not self_loops:
                if ind1 == ind2:
                    continue
            connectivity.append((min(ind1, ind2), max(ind1, ind2)))
            edges[(ind1, ind2)] = ei
    connectivity = list(set(connectivity))
    return nodes, edges, connectivity


def vertex_adjacency(solid, self_loops=False):
    """ 
    Creates a vertex adjacency graph from the given solid
    :param solid: A B-rep solid model of type occwl.Solid
    :param self_loops: Whether to add self loops in the graph (default: False)
    :return: list of vertices (occwl.Vertex), dict of edges (occwl.Edge), and a list of vertex index pairs for each edge in the graph.
             The indices in the connectivity index into the vertex list and can be used as keys in the edge dict. 
    """
    assert isinstance(solid, Solid)
    vert2ind = {}
    edge2ind = {}
    nodes = []
    edges = {}
    connectivity = []
    for i, vert in enumerate(solid.vertices()):
        vert2ind[vert.hash()] = i
        nodes.append(vert)

    for ei in solid.edges():
        connected_verts = list(solid.vertices_from_edge(ei))
        for (fi, fj) in itertools.permutations(connected_verts):
            ind1 = vert2ind[fi.hash()]
            ind2 = vert2ind[fj.hash()]
            if not self_loops:
                if ind1 == ind2:
                    continue
            connectivity.append((min(ind1, ind2), max(ind1, ind2)))
            edges[(ind1, ind2)] = ei
    connectivity = list(set(connectivity))
    return nodes, edges, connectivity

