from occwl.solid import Solid
from occwl.face import Face
from occwl.edge import Edge
#from occwl.vertex import Vertex
import itertools
import networkx as nx
from occwl.entity_mapper import EntityMapper


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
    mapper = EntityMapper(solid)
    graph = nx.Graph()
    for face in solid.faces():
        face_idx = mapper.face_index(face)
        graph.add_node(face, index=face_idx)

    for edge in solid.edges():
        connected_faces = list(solid.faces_from_edge(edge))
        if len(connected_faces) < 2:
            if edge.seam(connected_faces[0]) and self_loops:
                graph.add_edge(connected_faces[0], connected_faces[0])
        else:
            for (fi, fj) in itertools.permutations(connected_faces):
                edge_idx = mapper.edge_index(edge)
                graph.add_edge(fi, fj, edge=edge, index=edge_idx)
    return graph


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
    mapper = EntityMapper(solid)
    graph = nx.Graph()
    for vert in solid.vertices():
        vert_idx = mapper.vertex_index(vert)
        graph.add_node(vert, index=vert_idx)

    for edge in solid.edges():
        connected_verts = list(solid.vertices_from_edge(edge))
        if not edge.has_curve():
            continue
        if len(connected_verts) < 2:
            if edge.closed_edge() and self_loops:
                graph.add_edge(connected_verts[0], connected_verts[0])
        else:
            for (vi, vj) in itertools.permutations(connected_verts):
                edge_idx = mapper.edge_index(edge)
                graph.add_edge(vi, vj, edge=edge, index=edge_idx)
    return graph
