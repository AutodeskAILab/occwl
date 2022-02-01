import numpy as np

from OCC.Core.TopoDS import (
    TopoDS_Solid,
    TopoDS_Compound,
    TopoDS_CompSolid,
)
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pnt2d, gp_Ax2
import math
from occwl.base import VertexContainerMixin, EdgeContainerMixin, \
            WireContainerMixin, FaceContainerMixin, BottomUpFaceIterator, \
            BottomUpEdgeIterator, SurfacePropertiesMixin, VolumePropertiesMixin, \
            BoundingBoxMixin, TriangulatorMixin, ShellContainerMixin

from occwl.geometry import geom_utils
from occwl.shape import Shape
from deprecate import deprecated
import logging


class Solid(Shape, VertexContainerMixin, EdgeContainerMixin, ShellContainerMixin, \
            WireContainerMixin, FaceContainerMixin, BottomUpFaceIterator, \
            BottomUpEdgeIterator, SurfacePropertiesMixin, VolumePropertiesMixin, \
            BoundingBoxMixin, TriangulatorMixin):
    """
    A solid model
    """

    def __init__(self, shape, allow_compound=False):
        if allow_compound:
            assert (isinstance(shape, TopoDS_Solid) or 
                isinstance(shape, TopoDS_Compound) or 
                isinstance(shape, TopoDS_CompSolid))
        else:
            assert isinstance(shape, TopoDS_Solid)
        super().__init__(shape)

    @staticmethod
    def make_box(width, height, depth):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox

        return Solid(
            BRepPrimAPI_MakeBox(float(width), float(height), float(depth)).Shape()
        )

    @staticmethod
    def make_sphere(radius, center=(0, 0, 0)):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere

        return Solid(
            BRepPrimAPI_MakeSphere(geom_utils.to_gp_pnt(center), float(radius)).Shape()
        )

    @staticmethod
    def make_spherical_wedge(radius, center=(0, 0, 0), longitudinal_angle=2 * math.pi):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere

        return Solid(
            BRepPrimAPI_MakeSphere(
                geom_utils.to_gp_pnt(center), float(radius), float(longitudinal_angle)
            ).Shape()
        )

    @staticmethod
    def make_cone(
        radius_bottom,
        radius_top,
        height,
        apex_angle=2 * math.pi,
        base_point=(0, 0, 0),
        up_dir=(0, 0, 1),
    ):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCone

        return Solid(
            BRepPrimAPI_MakeCone(
                gp_Ax2(geom_utils.to_gp_pnt(base_point), geom_utils.to_gp_dir(up_dir)),
                float(radius_bottom),
                float(radius_top),
                float(height),
                float(apex_angle),
            ).Shape()
        )

    @staticmethod
    def make_cylinder(
        radius, height, angle=2 * math.pi, base_point=(0, 0, 0), up_dir=(0, 0, 1)
    ):
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder

        return Solid(
            BRepPrimAPI_MakeCylinder(
                gp_Ax2(geom_utils.to_gp_pnt(base_point), geom_utils.to_gp_dir(up_dir)),
                float(radius),
                float(height),
                float(angle),
            ).Shape()
        )

    def is_closed(self):
        """
        Checks and returns if the solid is closed (has no holes)

        Returns:
            bool: If closed
        """
        # In Open Cascade, unlinked (open) edges can be identified
        # as they appear in the edges iterator when ignore_orientation=False
        # but are not present in any wire
        ordered_edges = set()
        for wire in self.wires():
            for edge in wire.ordered_edges():
                ordered_edges.add(edge.topods_shape())
        unordered_edges = set([edge.topods_shape() for edge  in self.edges()])
        missing_edges = unordered_edges - ordered_edges
        return len(missing_edges) == 0

    def check_unique_oriented_edges(self):
        ordered_edges = set()
        for wire in self.wires():
            for oriented_edge in wire.ordered_edges():
                is_reversed = oriented_edge.reversed()
                tup = (oriented_edge, is_reversed)
               
                # We want to detect the case where the oriented
                # edges are not unique
                if tup in ordered_edges:
                    # Here we see the same oriented edges
                    # appears twice in the solid.  This is the 
                    # failure case we need to flag 
                    return False

                ordered_edges.add(tup)

        return True
