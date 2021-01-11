import numpy as np
from occam.face import Face
from occam.edge import Edge

def uvgrid_reverse_u(grid):
    reversed_grid = grid[::-1, :, :]
    return reversed_grid

def ugrid_reverse_u(grid):
    return grid[::-1, :]

def uvgrid(face, num_u=10, num_v=10):
    """ 
    Creates a 2D UV-grid of samples from the given face
    :param face: A B-rep face of type occam.Face
    :param num_u: Number of samples along u-direction (default: 10)
    :param num_v: Number of samples along v-direction (default: 10)
    """
    umin, umax, vmin, vmax = face.uv_bounds()
    print(umin, umax, vmin, vmax)

    u_step = (umax - umin) / (num_u - 1)
    v_step = (vmax - vmin) / (num_v - 1)

    uvgrid = np.zeros((num_u, num_v, 7), dtype=np.float32)
    for i in range(num_u):
        u = umin + float(i) * u_step
        for j in range(num_v):
            v = vmin + float(j) * v_step
            xyz = face.point(u, v)
            nor = face.normal(u, v)
            mask = int(face.inside(u, v))
            uvgrid[i, j, :3] = xyz
            uvgrid[i, j, 3:6] = nor
            uvgrid[i, j, 6] = mask

    if face.reversed():
        uvgrid = uvgrid_reverse_u(uvgrid)

    return uvgrid


def ugrid(edge, num_u: int =10):
    """ 
    Creates a 1D UV-grid of samples from the given edge
    :param face: A B-rep edge of type occam.Edge
    :param num_u: Number of samples along the curve (default: 10)
    """
    ugrid = np.zeros((num_u, 6), dtype=np.float32)

    if type(edge.curve()) is float:
        # Can't get an curve for this edge.   Let's return
        # the zero grid
        return ugrid

    umin, umax = edge.u_bounds()
    u_step = (umax - umin) / (num_u - 1)
    
    for i in range(num_u):
        u = umin + float(i) * u_step
        xyz = edge.point(u)
        tgt = edge.tangent(u)
        ugrid[i, :3] = xyz
        ugrid[i, 3:6] = tgt

    if edge.reversed():
        ugrid = ugrid_reverse_u(ugrid)

    return ugrid
