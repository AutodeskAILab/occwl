import numpy as np
from OCC.Core.gp import gp_Identity

from occwl.face import Face
from occwl.edge import Edge


def _uvgrid_reverse_u(grid):
    reversed_grid = grid[::-1, :, :]
    return reversed_grid


def _ugrid_reverse_u(grid):
    return grid[::-1, :]


def uvgrid(face, num_u=10, num_v=10, uvs=False, method="point", reverse_order_with_face=True):
    """ 
    Creates a 2D UV-grid of samples from the given face

    Args:
        face (occwl.face.Face): A B-rep face
        num_u (int): Number of samples along u-direction. Defaults to 10.
        num_v (int): Number of samples along v-direction. Defaults to 10.
        uvs (bool): Return the surface UVs where quantities are evaluated. Defaults to False.
        method (str): Name of the method in the occwl.face.Face object to be called 
                      (the method has to accept the uv value as argument). Defaults to "point".
    
    Returns:
        np.ndarray: 2D array of quantity evaluated on the face geometry
        np.ndarray (optional): 2D array of uv-values where evaluation was done
    """
    assert num_u >= 2
    assert num_v >= 2
    uv_box = face.uv_bounds()

    fn = getattr(face, method)

    uvgrid = []
    uv_values = np.zeros((num_u, num_v, 2), dtype=np.float32)

    if type(face.surface()) is float:
        # Can't get an curve for this face.
        if uvs:
            return None, uv_values
        return None

    for i in range(num_u):
        u = uv_box.intervals[0].interpolate(float(i) / (num_u - 1))
        for j in range(num_v):
            v = uv_box.intervals[1].interpolate(float(j) / (num_v - 1))
            uv = np.array([u, v])
            uv_values[i, j] = uv
            val = fn(uv)
            uvgrid.append(val)
    uvgrid = np.asarray(uvgrid).reshape((num_u, num_v, -1))

    if reverse_order_with_face:
        if face.reversed():
            uvgrid = _uvgrid_reverse_u(uvgrid)
            uv_values = _uvgrid_reverse_u(uv_values)

    if uvs:
        return uvgrid, uv_values
    return uvgrid


def ugrid(edge, num_u: int = 10, us=False, method="point", reverse_order_with_edge=True):
    """ 
    Creates a 1D UV-grid of samples from the given edge
        edge (occwl.edge.Edge): A B-rep edge
        num_u (int): Number of samples along the curve. Defaults to 10/
        us (bool): Return the u values at which the quantity were evaluated
        method (str): Name of the method in the occwl.edge.Edge object to be called 
                      (the method has to accept the u value as argument). Defaults to "point".
    Returns:
        np.ndarray: 1D array of quantity evaluated on the edge geometry
        np.ndarray (optional): 1D array of u-values where evaluation was done
    """
    assert num_u >= 2
    ugrid = []
    u_values = np.zeros((num_u), dtype=np.float32)

    if type(edge.curve()) is float:
        # Can't get an curve for this edge.
        if us:
            return None, u_values
        return None

    bound = edge.u_bounds()
    fn = getattr(edge, method)

    for i in range(num_u):
        u = bound.interpolate(float(i) / (num_u - 1))
        u_values[i] = u
        val = fn(u)
        ugrid.append(val)

    ugrid = np.asarray(ugrid).reshape((num_u, -1))
    if reverse_order_with_edge:
        if edge.reversed():
            ugrid = _ugrid_reverse_u(ugrid)
            u_values = u_values[::-1]
    if us:
        return ugrid, u_values
    return ugrid
