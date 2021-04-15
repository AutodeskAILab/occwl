import numpy as np
from occwl.face import Face
from occwl.edge import Edge

def _uvgrid_reverse_u(grid):
    reversed_grid = grid[::-1, :, :]
    return reversed_grid

def _ugrid_reverse_u(grid):
    return grid[::-1, :]

def uvgrid(face, num_u=10, num_v=10, uvs=False):
    """ 
    Creates a 2D UV-grid of samples from the given face
    :param face: A B-rep face of type occwl.Face
    :param num_u: Number of samples along u-direction (default: 10)
    :param num_v: Number of samples along v-direction (default: 10)
    :param uvs: Return the surface UVs at which the points and normals
                where evaluated
    """
    assert num_u >= 2
    assert num_v >= 2
    uv_box = face.uv_bounds()

    uvgrid = np.zeros((num_u, num_v, 7), dtype=np.float32)
    uv_values = np.zeros((num_u, num_v, 2), dtype=np.float32)
    for i in range(num_u):
        u = uv_box.intervals[0].interpolate(float(i)/(num_u - 1))
        for j in range(num_v):
            v = uv_box.intervals[1].interpolate(float(j)/(num_v - 1))
            uv_values[i,j, 0] = u
            uv_values[i,j, 1] = v
            uv = np.array([u, v])
            xyz = face.point(uv)
            nor = face.normal(uv)
            mask = int(face.inside(uv))
            uvgrid[i, j, :3] = xyz
            uvgrid[i, j, 3:6] = nor
            uvgrid[i, j, 6] = mask

    if face.reversed():
        uvgrid = _uvgrid_reverse_u(uvgrid)
        uv_values = _uvgrid_reverse_u(uv_values)

    if uvs:
        return uvgrid, uv_values
    return uvgrid


def ugrid(edge, num_u: int =10, us=False):
    """ 
    Creates a 1D UV-grid of samples from the given edge
    :param face: A B-rep edge of type occwl.Edge
    :param num_u: Number of samples along the curve (default: 10)
    :param us: Return the u values at which the points were evaluated
    """
    ugrid = np.zeros((num_u, 6), dtype=np.float32)
    u_values = np.zeros((num_u), dtype=np.float32)

    if type(edge.curve()) is float:
        # Can't get an curve for this edge.   Let's return
        # the zero grid
        if us:
            return ugrid, u_values
        return ugrid

    bound = edge.u_bounds()
    
    for i in range(num_u):
        u = bound.interpolate(float(i)/(num_u-1))
        u_values[i] = u
        xyz = edge.point(u)
        tgt = edge.tangent(u)
        ugrid[i, :3] = xyz
        ugrid[i, 3:6] = tgt

    if edge.reversed():
        ugrid = _ugrid_reverse_u(ugrid)
        u_values = u_values[::-1]
    if us:
        return ugrid, u_values
    return ugrid