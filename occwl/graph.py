from occwl.solid import Solid
from occwl.face import Face
from occwl.edge import Edge
#from occwl.vertex import Vertex
import itertools


def face_adjacency(solid, self_loops=False):
    """
    Creates a face adjacency graph from the given solid

    Args:
        solid (occwl.solid.Solid): Solid model
        self_loops (bool, optional): Whether to add self loops in the graph. Defaults to False.
        
    Returns:
        List[occwl.face.Face]: list of faces
        Dict[(int, int), occwl.edge.Edge]: mapping from face pairs to edge that lies in-between them
        List[(int, int)]: Indices into the face list; can be used as keys in the edge dict.
    """
    assert isinstance(solid, Solid)
    face2ind = {}
    nodes = []
    edges = {}
    connectivity = []
    for i, face in enumerate(solid.faces()):
        face2ind[face] = i
        nodes.append(face)

    for ei in solid.edges():
        connected_faces = list(solid.faces_from_edge(ei))
        for (fi, fj) in itertools.permutations(connected_faces):
            ind1 = face2ind[fi]
            ind2 = face2ind[fj]
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

    Args:
        solid (occwl.solid.Solid): Solid model
        self_loops (bool, optional): Whether to add self loops in the graph. Defaults to False.
    
    Returns:
        List[occwl.vertex.Vertex]: list of vertices
        Dict[(int, int), occwl.edge.Edge]: mapping from vertex pairs to edge that lies in-between them
        List[(int, int)]: Indices into the vertex list; can be used as keys in the edge dict.
    """
    assert isinstance(solid, Solid)
    vert2ind = {}
    nodes = []
    edges = {}
    connectivity = []
    for i, vert in enumerate(solid.vertices()):
        vert2ind[vert] = i
        nodes.append(vert)

    for ei in solid.edges():
        connected_verts = list(solid.vertices_from_edge(ei))
        for (vi, vj) in itertools.permutations(connected_verts):
            ind1 = vert2ind[vi]
            ind2 = vert2ind[vj]
            if not self_loops:
                if ind1 == ind2:
                    continue
            connectivity.append((min(ind1, ind2), max(ind1, ind2)))
            edges[(ind1, ind2)] = ei
    connectivity = list(set(connectivity))
    return nodes, edges, connectivity
