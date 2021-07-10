import numpy as np
from OCC.Core.gp import gp_Pnt, gp_Pnt2d, gp_Vec, gp_Dir


def tuple_to_numpy(tup):
    l = list(tup)
    return np.array(l)


def gp_to_numpy(gp):
    if isinstance(gp, gp_Pnt2d):
        return np.array([gp.X(), gp.Y()])
    elif isinstance(gp, (gp_Pnt, gp_Dir, gp_Vec)):
        return np.array([gp.X(), gp.Y(), gp.Z()])
    raise NotImplementedError


def numpy_to_gp(np_point):
    assert np_point.size == 3
    return gp_Pnt(float(np_point[0]), float(np_point[1]), float(np_point[2]))


def numpy_to_gp_vec(np_vec):
    assert np_vec.size == 3
    return gp_Vec(float(np_vec[0]), float(np_vec[1]), float(np_vec[2]))


def numpy_to_gp_dir(np_vec):
    assert np_vec.size == 3
    return gp_Dir(float(np_vec[0]), float(np_vec[1]), float(np_vec[2]))
