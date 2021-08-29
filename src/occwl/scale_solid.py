"""
Utility function to scale a solid body into a box 
[-1, 1]^3
"""
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from deprecate import deprecated
import logging

# occwl
from occwl.solid import Solid
from occwl.geometry import geom_utils

@deprecated(
    target=None, deprecated_in="0.01", remove_in="0.03", stream=logging.warning
)
def scale_solid_to_unit_box(solid):
    """
    Translate and scale the given solid so it fits exactly 
    into the [-1, 1]^3 box

    Args:
        solid (occwl.Solid) The solid to scale

    Returns:
        occwl.Solid The scaled solid
    """
    # Get an exact box for the solid
    box = solid.exact_box()
    center = box.center()
    longest_length = box.max_box_length()

    orig = gp_Pnt(0.0, 0.0, 0.0)
    center = geom_utils.numpy_to_gp(center)
    vec_center_to_orig = gp_Vec(center, orig)
    move_to_center = gp_Trsf()
    move_to_center.SetTranslation(vec_center_to_orig)

    scale_trsf = gp_Trsf()
    scale_trsf.SetScale(orig, 2.0/longest_length)
    trsf_to_apply = scale_trsf.Multiplied(move_to_center)
    
    apply_transform = BRepBuilderAPI_Transform(trsf_to_apply)
    apply_transform.Perform(solid.topods_shape())
    transformed_solid = apply_transform.ModifiedShape(solid.topods_shape())

    return Solid(transformed_solid)



