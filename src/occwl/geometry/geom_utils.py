import numpy as np
from OCC.Core.gp import gp_Pnt, gp_Pnt2d, gp_Vec, gp_Dir, gp_Ax1, gp_Trsf

from occwl.geometry.box import Box

def tuple_to_numpy(tup):
    l = list(tup)
    return np.array(l)


def gp_to_numpy(gp):
    if isinstance(gp, gp_Pnt2d):
        return np.array([gp.X(), gp.Y()])
    elif isinstance(gp, (gp_Pnt, gp_Dir, gp_Vec)):
        return np.array([gp.X(), gp.Y(), gp.Z()])
    raise NotImplementedError

def box_to_geometry(bnd_box):
    max_corner = bnd_box.CornerMax()
    min_corner = bnd_box.CornerMin()
    bb = Box(gp_to_numpy(min_corner))
    bb.encompass_point(gp_to_numpy(max_corner))
    return bb

def numpy_to_gp(np_point):
    assert np_point.size == 3
    return gp_Pnt(float(np_point[0]), float(np_point[1]), float(np_point[2]))


def numpy_to_gp_vec(np_vec):
    assert np_vec.size == 3
    return gp_Vec(float(np_vec[0]), float(np_vec[1]), float(np_vec[2]))


def numpy_to_gp_dir(np_vec):
    assert np_vec.size == 3
    return gp_Dir(float(np_vec[0]), float(np_vec[1]), float(np_vec[2]))


def to_numpy(any_2d_or_3d_type, dtype=np.float32):
    if isinstance(any_2d_or_3d_type, gp_Pnt2d):
        return np.array([any_2d_or_3d_type.X(), any_2d_or_3d_type.Y()], dtype=dtype)
    elif isinstance(any_2d_or_3d_type, (gp_Pnt, gp_Dir, gp_Vec)):
        return np.array(
            [any_2d_or_3d_type.X(), any_2d_or_3d_type.Y(), any_2d_or_3d_type.Z()],
            dtype=dtype,
        )
    elif isinstance(any_2d_or_3d_type, (tuple, list)):
        if len(any_2d_or_3d_type) == 3:
            return np.array(
                [any_2d_or_3d_type[0], any_2d_or_3d_type[1], any_2d_or_3d_type[2]],
                dtype=dtype,
            )
        elif len(any_2d_or_3d_type) == 2:
            return np.array([any_2d_or_3d_type[0], any_2d_or_3d_type[1]], dtype=dtype)
    elif isinstance(any_2d_or_3d_type, gp_Trsf):
        # Convert the transform into a 4x4 homogeneous transform matrix
        mat = np.eye(4)
        for i in range(3):
            for j in range(4):
                mat[i,j] = any_2d_or_3d_type.Value(i+1,j+1)
        return mat
    raise ValueError(f"Unexpected type: {type(any_2d_or_3d_type)}")


def to_gp_pnt(any_2d_or_3d_type):
    assert len(any_2d_or_3d_type) == 2 or len(any_2d_or_3d_type) == 3
    if len(any_2d_or_3d_type) == 3:
        return gp_Pnt(
            float(any_2d_or_3d_type[0]),
            float(any_2d_or_3d_type[1]),
            float(any_2d_or_3d_type[2]),
        )
    elif len(any_2d_or_3d_type) == 2:
        return gp_Pnt2d(float(any_2d_or_3d_type[0]), float(any_2d_or_3d_type[1]))
    raise ValueError(
        f"Unexpected length: {len(any_2d_or_3d_type)}. Need 2d or 3d subscriptable objects."
    )


def to_gp_dir(any_3d_type):
    assert len(any_3d_type) == 3
    return gp_Dir(float(any_3d_type[0]), float(any_3d_type[1]), float(any_3d_type[2]))


def to_gp_vec(any_3d_type):
    assert len(any_3d_type) == 3
    return gp_Vec(float(any_3d_type[0]), float(any_3d_type[1]), float(any_3d_type[2]))


def to_gp_axis(point_3d, dir_3d):
    assert len(point_3d) == 3
    assert len(dir_3d) == 3
    return gp_Ax1(to_gp_pnt(point_3d), to_gp_dir(dir_3d))

def is_geometric_identity(transform):
    assert isinstance(transform, gp_Trsf), "Must be a gp_Trsf"
    np_tsf = to_numpy(transform)
    return np.allclose(np_tsf, np.eye(4))