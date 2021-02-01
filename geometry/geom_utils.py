import numpy as np

def tuple_to_numpy(tup):
    l = list(tup)
    return np.array(l)

def gp_Pnt_to_numpy(pnt):
    return np.array([pnt.X(), pnt.Y(), pnt.Z()])