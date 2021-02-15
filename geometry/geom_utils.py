import numpy as np
from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Dir

def tuple_to_numpy(tup):
    l = list(tup)
    return np.array(l)

def gp_to_numpy(gp):
    return np.array([gp.X(), gp.Y(), gp.Z()])

def numpy_to_gp(np_point):
    assert np_point.size == 3
    return gp_Pnt(np_point[0], np_point[1], np_point[2])

def numpy_to_gp_vec(np_vec):
    assert np_vec.size == 3
    return gp_Vec(np_vec[0], np_vec[1], np_vec[2])

def numpy_to_gp_dir(np_vec):
    assert np_vec.size == 3
    return gp_Dir(
        float(np_vec[0]), 
        float(np_vec[1]),
        float(np_vec[2])
    )
