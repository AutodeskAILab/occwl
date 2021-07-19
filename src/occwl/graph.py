from occwl.solid import Solid
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
        nx.Graph: Each B-rep face is mapped to a node with its index and each B-rep edge is mapped to an edge in the graph
                  Node attributes:
                  - "face": contains the B-rep face
                  Edge attributes:
                  - "edge": contains the B-rep edge
                  - "edge_idx": index of the edge in the solid
    """
    assert isinstance(solid, Solid)
    mapper = EntityMapper(solid)
    graph = nx.Graph()
    for face in solid.faces():
        face_idx = mapper.face_index(face)
        graph.add_node(face_idx, face=face)

    for edge in solid.edges():
        connected_faces = list(solid.faces_from_edge(edge))
        if len(connected_faces) < 2:
            if edge.seam(connected_faces[0]) and self_loops:
                face_idx = mapper.face_index(connected_faces[0])
                graph.add_edge(face_idx, face_idx)
        else:
            for (face_i, face_j) in itertools.permutations(connected_faces):
                face_i_index = mapper.face_index(face_i)
                face_j_index = mapper.face_index(face_j)
                edge_idx = mapper.edge_index(edge)
                graph.add_edge(
                    face_i_index, face_j_index, edge=edge, edge_index=edge_idx
                )
    return graph


def vertex_adjacency(solid, self_loops=False):
    """ 
    Creates a vertex adjacency graph from the given solid

    Args:
        solid (occwl.solid.Solid): Solid model
        self_loops (bool, optional): Whether to add self loops in the graph. Defaults to False.
    
    Returns:
        nx.Graph: Each B-rep vertex is mapped to a node with its index and each B-rep edge is mapped to an edge in the graph
                  Node attributes:
                  - "vertex": contains the B-rep vertex
                  Edge attributes:
                  - "edge": contains the B-rep edge
                  - "edge_idx": index of the edge in the solid
    """
    assert isinstance(solid, Solid)
    mapper = EntityMapper(solid)
    graph = nx.Graph()
    for vert in solid.vertices():
        vert_idx = mapper.vertex_index(vert)
        graph.add_node(vert_idx, vertex=vert)

    for edge in solid.edges():
        connected_verts = list(solid.vertices_from_edge(edge))
        if not edge.has_curve():
            continue
        if len(connected_verts) < 2:
            if edge.closed_edge() and self_loops:
                vert_idx = mapper.vertex_index(connected_verts[0])
                graph.add_edge(vert_idx, vert_idx)
        else:
            for (vert_i, vert_j) in itertools.permutations(connected_verts):
                edge_idx = mapper.edge_index(edge)
                vert_i_index = mapper.vertex_index(vert_i)
                vert_j_index = mapper.vertex_index(vert_j)
                graph.add_edge(
                    vert_i_index, vert_j_index, edge=edge, edge_index=edge_idx
                )
    return graph
