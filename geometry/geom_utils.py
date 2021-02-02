import numpy as np

def tuple_to_numpy(tup):
    l = list(tup)
    return np.array(l)

def gp_to_numpy(gp):
    return np.array([gp.X(), gp.Y(), gp.Z()])