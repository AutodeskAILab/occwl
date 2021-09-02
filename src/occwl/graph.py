from occwl.solid import Solid
import networkx as nx
from occwl.entity_mapper import EntityMapper


def face_adjacency(solid, self_loops=False):
    """
    Creates a face adjacency graph from the given solid

    Args:
        solid (occwl.solid.Solid): Solid model
        self_loops (bool, optional): Whether to add self loops in the graph. Defaults to False.
        
    Returns:
        nx.DiGraph: Each B-rep face is mapped to a node with its index and each B-rep edge is mapped to an edge in the graph
                    Node attributes:
                    - "face": contains the B-rep face
                    Edge attributes:
                    - "edge": contains the B-rep (ordered) edge
                    - "edge_idx": index of the (ordered) edge in the solid
        None: if the solid is non-manifold or open
    """
    assert isinstance(solid, Solid)
    # Return None if the solid is not closed i.e. has holes
    # TODO(pradeep): this should be accommodated in future
    if not solid.is_closed():
        return None
    mapper = EntityMapper(solid)
    graph = nx.DiGraph()
    for face in solid.faces():
        face_idx = mapper.face_index(face)
        graph.add_node(face_idx, face=face)

    for edge in solid.edges():
        if not edge.has_curve():
            continue
        connected_faces = list(solid.faces_from_edge(edge))
        if len(connected_faces) < 2:
            if edge.seam(connected_faces[0]) and self_loops:
                face_idx = mapper.face_index(connected_faces[0])
                graph.add_edge(face_idx, face_idx)
        elif len(connected_faces) == 2:
            left_face, right_face = edge.find_left_and_right_faces(connected_faces)
            if left_face is None or right_face is None:
                continue
            edge_idx = mapper.oriented_edge_index(edge)
            edge_reversed = edge.reversed_edge()
            if not mapper.oriented_edge_exists(edge_reversed):
                continue
            edge_reversed_idx = mapper.oriented_edge_index(edge_reversed)
            left_index = mapper.face_index(left_face)
            right_index = mapper.face_index(right_face)
            graph.add_edge(left_index, right_index, edge=edge, edge_index=edge_idx) 
            graph.add_edge(right_index, left_index, edge=edge_reversed, edge_index=edge_reversed_idx)
        else:
            raise RuntimeError("Expected a manifold, an edge must be incident on one/two faces")
    return graph


def vertex_adjacency(solid, self_loops=False):
    """ 
    Creates a vertex adjacency graph from the given solid

    Args:
        solid (occwl.solid.Solid): Solid model
        self_loops (bool, optional): Whether to add self loops in the graph. Defaults to False.
    
    Returns:
        nx.DiGraph: Each B-rep vertex is mapped to a node with its index and each B-rep edge is mapped to an edge in the graph
                    Node attributes:
                    - "vertex": contains the B-rep vertex
                    Edge attributes:
                    - "edge": contains the B-rep (ordered) edge
                    - "edge_idx": index of the (ordered) edge in the solid
    """
    assert isinstance(solid, Solid)
    mapper = EntityMapper(solid)
    graph = nx.DiGraph()
    for vert in solid.vertices():
        vert_idx = mapper.vertex_index(vert)
        graph.add_node(vert_idx, vertex=vert)

    for edge in solid.edges():
        connected_verts = list(solid.vertices_from_edge(edge))
        if not edge.has_curve():
            continue
        if len(connected_verts) == 1:
            if edge.closed_edge() and self_loops:
                vert_idx = mapper.vertex_index(connected_verts[0])
                graph.add_edge(vert_idx, vert_idx)
        elif len(connected_verts) == 2:
            # Don't add an edge if the edge doesn't exist in the model
            if not mapper.oriented_edge_exists(edge):
                continue
            edge_idx = mapper.oriented_edge_index(edge)
            edge_reversed = edge.reversed_edge()
            if not mapper.oriented_edge_exists(edge_reversed):
                continue
            edge_reversed_idx = mapper.oriented_edge_index(edge_reversed)
            vert_i_index = mapper.vertex_index(edge.start_vertex())
            vert_j_index = mapper.vertex_index(edge.end_vertex())
            graph.add_edge(
                vert_i_index, vert_j_index, edge=edge, edge_index=edge_idx
            )
            graph.add_edge(
                vert_j_index, vert_i_index, edge=edge_reversed, edge_index=edge_reversed_idx
            )
        else:
            raise RuntimeError("Expected an edge two connected one/two vertices")

    return graph
