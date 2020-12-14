import numpy as np
from occam.face import Face


def uvgrid(face: Face, num_u:int =10, num_v: int=10):
    """ 
    Creates a UV-grid of samples from the given face
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
    return uvgrid


def ugrid(edge, num_u=10):
    pass

