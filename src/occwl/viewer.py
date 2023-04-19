from datetime import datetime
from typing import Any, Callable, List, Optional, Tuple

import numpy as np
from OCC.Core.AIS import AIS_Line, AIS_Point, AIS_Shaded, AIS_WireFrame, AIS_Axis
from OCC.Core.Aspect import (
    Aspect_TOL_DASH,
    Aspect_TOL_DOT,
    Aspect_TOL_DOTDASH,
    Aspect_TOL_SOLID,
    Aspect_TOM_BALL,
    Aspect_TOM_O,
    Aspect_TOM_POINT,
    Aspect_TOM_STAR,
    Aspect_TOM_X,
)
from OCC.Core.Graphic3d import (
    Graphic3d_TOSM_VERTEX,
    Graphic3d_TOSM_FACET,
    Graphic3d_TOSM_FRAGMENT
)
from OCC.Core.gp import gp_Ax1, gp_Dir
from OCC.Core.Geom import Geom_CartesianPoint, Geom_Line
from OCC.Core.Prs3d import Prs3d_LineAspect, Prs3d_PointAspect
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.TopAbs import (
    TopAbs_EDGE,
    TopAbs_FACE,
    TopAbs_SHELL,
    TopAbs_SOLID,
    TopAbs_VERTEX,
)
from OCC.Core.TopoDS import (
    TopoDS_Edge,
    TopoDS_Face,
    TopoDS_Shell,
    TopoDS_Solid,
    TopoDS_Vertex,
    TopoDS_Compound,
)
from OCC.Core.V3d import V3d_DirectionalLight
from OCC.Display.SimpleGui import init_display
from OCC.Display.OCCViewer import get_color_from_name
from OCC.Display.OCCViewer import Viewer3d

from occwl.edge import Edge
from occwl.face import Face
from occwl.wire import Wire
from occwl.geometry import geom_utils
from occwl.solid import Solid
from occwl.vertex import Vertex
from occwl.compound import Compound
from occwl.shell import Shell


def _get_quantity_color(color):
    assert isinstance(color, (list, tuple))
    assert len(color) == 3
    r, g, b = color
    assert type(r) == type(g) == type(b)
    assert type(r) in (float, int)
    if type(r) == int:
        assert 0 <= r <= 255
        assert 0 <= g <= 255
        assert 0 <= b <= 255
        return Quantity_Color(r / 255.0, g / 255.0, b / 255.0, Quantity_TOC_RGB)
    assert 0.0 <= r <= 1.0
    assert 0.0 <= g <= 1.0
    assert 0.0 <= b <= 1.0
    return Quantity_Color(r, g, b, Quantity_TOC_RGB)


class _BaseViewer:
    def display(self, shape, update=False, color=None, transparency=0.0):
        """
        Display a shape (must be a Solid, Face, or Edge)

        Args:
            shape (Solid, Face, or Edge): Shape to display
            update (bool, optional): Whether to update and repaint. Defaults to False.
            color (str or tuple, optional): Color of the shape.
                                            If str, can be 'WHITE', 'BLUE', 'RED', 'GREEN', 'YELLOW',
                                           'CYAN', 'BLACK', or 'ORANGE'. Defaults to None.
            transparency (float, optional): How transparent the shape is. Defaults to 0.0.
        """
        if isinstance(shape, (Compound, Solid, Shell, Face, Edge, Wire, Vertex)):
            shape = shape.topods_shape()
        if color and not isinstance(color, (str, tuple)):
            color = "BLACK"
        if isinstance(color, (tuple, list)):
            assert len(color) == 3, "Expected a 3-tuple/list when color is specified as RGB"
            color = Quantity_Color(
                float(color[0]), float(color[1]), float(color[2]), Quantity_TOC_RGB
            )
        return self._display.DisplayShape(
            shape, update=update, color=color, transparency=transparency
        )

    def display_text(self, xyz, text, height=None, color=None):
        """
        Display a text

        Args:
            xyz (tuple of floats or 1D np.ndarray of 2 or 3): Coordinate in model space where text would appear
            text (str): Text to display
            height (float, optional): Height of the text font. Defaults to None.
            color (tuple of 3 floats, optional): RGB color. Defaults to None.
        """
        return self._display.DisplayMessage(
            geom_utils.to_gp_pnt(xyz), text, height=height, message_color=color
        )

    def display_points(self, pts, color=None, scale=10, marker="ball"):
        """
        Display a set of points

        Args:
            points (np.ndarray #points x 3): Points to display
            color (tuple of 3 floats or np.ndarray of size #points x 3 or str, optional): RGB color (can be a single color or per-point colors). Defaults to None.
            scale (float, optional): Scale of the points
            marker (str, optional): Marker type for the point. Must be one of ('point', 'star', 'ball', 'x', 'o'). Defaults to 'ball'.
        """
        if color is None:
            color = (0, 0, 0)
        if marker == "point":
            marker_type = Aspect_TOM_POINT
        elif marker == "o":
            marker_type = Aspect_TOM_O
        elif marker == "star":
            marker_type = Aspect_TOM_STAR
        elif marker == "x":
            marker_type = Aspect_TOM_X
        elif marker == "ball":
            marker_type = Aspect_TOM_BALL
        else:
            marker_type = Aspect_TOM_POINT
            print(
                "Unknown marker type {}. Expected one of ('point', 'star', 'ball', 'o', 'x'). Setting to 'point'."
            )
        point_entities = []
        for idx in range(pts.shape[0]):
            if isinstance(color, tuple):
                quantity_color = Quantity_Color(color[0], color[1], color[2], Quantity_TOC_RGB)
            elif isinstance(color, np.ndarray):
                assert (
                    pts.shape[0] == color.shape[0]
                ), "pts and color must match in size (#points x 3)"
                quantity_color = Quantity_Color(
                    color[idx, 0], color[idx, 1], color[idx, 2], Quantity_TOC_RGB
                )
            elif isinstance(color, str):
                quantity_color = get_color_from_name(color)
            p = Geom_CartesianPoint(geom_utils.to_gp_pnt(pts[idx, :]))
            ais_point = AIS_Point(p)
            attr = ais_point.Attributes()
            asp = Prs3d_PointAspect(marker_type, quantity_color, float(scale))
            attr.SetPointAspect(asp)
            ais_point.SetAttributes(attr)
            self._display.Context.Display(ais_point, False)
            point_entities.append(ais_point)
        return point_entities

    def display_lines(
        self, origins, directions, color=None, thickness=1, style="solid",
    ):
        """
        Display a set of lines

        Args:
            origins (2D np.ndarray of size #points x 3): Origin points of the arrows
            directions (2D np.ndarray of size #points x 3): Unit vectors for directions of the arrows
            color (tuple of 3 floats or 2D np.ndarray of size #points x 3 or str, optional): RGB color (can be a single color or per-point colors). Defaults to None.
            thickness (float, optional): Thickness of the lines
            style (str, optional): Style for the lines. Must be one of ('solid', 'dash', 'dot', 'dotdash'). Defaults to 'solid'.
        """
        assert (
            origins.shape[0] == directions.shape[0]
        ), "origins and directions must match in size (#points x 3)"
        if color is None:
            color = (0, 0, 0)

        if style == "solid":
            type_of_line = Aspect_TOL_SOLID
        elif style == "dash":
            type_of_line = Aspect_TOL_DASH
        elif style == "dot":
            type_of_line = Aspect_TOL_DOT
        elif style == "dotdash":
            type_of_line = Aspect_TOL_DOTDASH
        else:
            type_of_line = Aspect_TOL_SOLID
            print(
                f"Unknown style {style}. Expected one of ('solid', 'dash', 'dot', 'dotdash'). Setting to 'solid'."
            )

        line_entities = []
        for idx in range(origins.shape[0]):
            if isinstance(color, tuple):
                quantity_color = Quantity_Color(color[0], color[1], color[2], Quantity_TOC_RGB)
            elif isinstance(color, np.ndarray):
                assert (
                    origins.shape[0] == color.shape[0]
                ), "pts and color must match in size (#points x 3)"
                quantity_color = Quantity_Color(
                    color[idx, 0], color[idx, 1], color[idx, 2], Quantity_TOC_RGB
                )
            elif isinstance(color, str):
                quantity_color = get_color_from_name(color)

            line = Geom_Line(
                geom_utils.to_gp_pnt(origins[idx, :]),
                geom_utils.to_gp_dir(directions[idx, :]),
            )
            ais_line = AIS_Line(line)
            attr = ais_line.Attributes()
            asp = Prs3d_LineAspect(quantity_color, type_of_line, thickness)
            attr.SetLineAspect(asp)
            ais_line.SetAttributes(attr)
            self._display.Context.Display(ais_line, False)
            line_entities.append(ais_line)
        return line_entities

    def _convert_to_occwl_types(self, shapes):
        for i in range(len(shapes)):
            if type(shapes[i]) == TopoDS_Vertex:
                shapes[i] = Vertex(shapes[i])
            elif type(shapes[i]) == TopoDS_Edge:
                shapes[i] = Edge(shapes[i])
            elif type(shapes[i]) == TopoDS_Face:
                shapes[i] = Face(shapes[i])
            elif type(shapes[i]) == TopoDS_Solid:
                shapes[i] = Solid(shapes[i])
        return shapes

    def selected_shapes(self):
        """
        Get the selected shapes

        Returns:
            List[TopoDS_Shape]: List of selected shapes
        """
        shapes = self._display.GetSelectedShapes()
        shapes = self._convert_to_occwl_types(shapes)
        return shapes
    
    def clear(self):
        """
        Clear all shapes from the viewer
        """
        self._display.EraseAll()

    def fit(self):
        """
        Fit the camera to the scene
        """
        self._display.FitAll()

    def perspective(self):
        """
        Set perspective camera projection
        """
        self._display.SetPerspectiveProjection()
        self._display.FitAll()

    def orthographic(self):
        """
        Set orthographic camera projection
        """
        self._display.SetOrthographicProjection()
        self._display.FitAll()

    def wireframe(self):
        """
        Set all shapes to appear as wireframes
        """
        self._display.View.SetComputedMode(False)
        self._display.Context.SetDisplayMode(AIS_WireFrame, True)

    def shaded(self):
        """
        Shade all shapes
        """
        self._display.View.SetComputedMode(False)
        self._display.Context.SetDisplayMode(AIS_Shaded, True)

    def save_image(self, filename=None):
        """
        Save a screenshot of the viewer

        Args:
            filename (str or pathlib.Path, optional): Image file to save the screenshot. Defaults to None.
                                                      If None, writes a PNG file named with the current timestamp
        """
        if filename is None:
            now = datetime.now()
            current_time = str(now)
            filename = current_time + ".png"
        self._display.View.Dump(str(filename))

    def use_rasterization(self):
        """
        Render using rasterization
        """
        self._display.SetRasterizationMode()

    def use_raytracing(self, depth=3):
        """
        Render using raytracing

        Args:
            depth (int, optional): Number of bounces for rays Defaults to 3.
        """
        self._display.SetRaytracingMode(depth=depth)
    
    def show_axes(self):
        """
        Show the XYZ-axes widget
        """
        self._display.display_triedron()

    def hide_axes(self):
        """
        Hide the XYZ-axes widget
        """
        self._display.hide_triedron()
    
    def enable_antialiasing(self):
        """
        Enable antialiasing
        """
        self._display.EnableAntiAliasing()
    
    def disable_antialiasing(self):
        """
        Disable antialiasing
        """
        self._display.DisableAntiAliasing()
    
    def set_background_color(self, top_color, bottom_color):
        """
        Set the background gradient color

        Args:
            top_color (List/Tuple[int, int, int]): Top color
            bottom_color (List/Tuple[int, int, int]): Bottom color
        """
        assert isinstance(top_color, (tuple, list))
        assert isinstance(bottom_color, (tuple, list))
        self._display.set_bg_gradient_color(top_color, bottom_color)
    
    def show_face_boundary(self):
        """
        Show the edges bounding each face
        """
        self._display.default_drawer.SetFaceBoundaryDraw(True)

    def hide_face_boundary(self):
        """
        Hide the edges bounding each face
        """
        self._display.default_drawer.SetFaceBoundaryDraw(False)
    
    def set_size(self, width, height):
        """
        Set the size of the framebuffer

        Args:
            width (int): Width of the framebuffer
            height (int): Height of the framebuffer
        """
        self._display.SetSize(width, height)
    
    def use_gouraud_shading(self):
        """
        Compute colors per vertex and interpolate
        """
        self._display.View.SetShadingModel(Graphic3d_TOSM_VERTEX)
    
    def use_flat_shading(self):
        """
        Use no interpolation when computing color for fragments in a triangle
        """
        self._display.View.SetShadingModel(Graphic3d_TOSM_FACET)

    def use_phong_shading(self):
        """
        Compute colors per fragment
        """
        self._display.View.SetShadingModel(Graphic3d_TOSM_FRAGMENT)

    def add_directional_light(self, direction, color, intensity=500.0):
        assert len(direction) == 3
        assert len(color) == 3
        color = _get_quantity_color(color)
        dir_light = V3d_DirectionalLight(gp_Dir(*direction), color)
        dir_light.SetEnabled(True)
        dir_light.SetIntensity(intensity)
        self._display.Viewer.AddLight(dir_light)
        self._display.Viewer.SetLightOn()


class Viewer(_BaseViewer):
    """
    A Viewer for topological entities
    """

    def __init__(
        self,
        backend: str = None,
        size: Optional[Tuple[int, int]] = (1024, 768),
        axes: Optional[bool] = True,
        background_gradient_color1: Optional[List[int]] = [206, 215, 222],
        background_gradient_color2: Optional[List[int]] = [128, 128, 128],
    ):
        """
        Construct the Viewer

        Args:
            backend (str, optional): Backend use to create the viewer. Must be one of wx, pyqt4, pyqt5 or pyside. Defaults to None.
            size (Optional[Tuple[int, int]], optional): Size of the viewer window. Defaults to (1024, 768).
            axes (Optional[bool], optional): Show arrows for coordinate axes. Defaults to True.
            background_gradient_color1 (Optional[List[int]], optional): Background color at the top. Defaults to [206, 215, 222].
            background_gradient_color2 (Optional[List[int]], optional): Background color at the bottom. Defaults to [128, 128, 128].
        """
        (
            self._display,
            self._start_display,
            self._add_menu,
            self._add_function_to_menu,
        ) = init_display(
            backend_str=backend,
            size=size,
            display_triedron=axes,
            background_gradient_color1=background_gradient_color1,
            background_gradient_color2=background_gradient_color2,
        )

    def on_select(self, callback):
        """
        Callback to execute when a selection is made

        Args:
            callback (function): Called when a selection is made. Must have signature:
                                 def callback(selected_shapes, mouse_x, mouse_y)
        """

        def wrapped_callback(selected_shapes, x, y):
            selected_shapes = self._convert_to_occwl_types(selected_shapes)
            return callback(selected_shapes, x, y)

        self._display.register_select_callback(wrapped_callback)

    def _convert_to_occwl_types(self, shapes):
        for i in range(len(shapes)):
            if type(shapes[i]) == TopoDS_Vertex:
                shapes[i] = Vertex(shapes[i])
            elif type(shapes[i]) == TopoDS_Edge:
                shapes[i] = Edge(shapes[i])
            elif type(shapes[i]) == TopoDS_Face:
                shapes[i] = Face(shapes[i])
            elif type(shapes[i]) == TopoDS_Shell:
                shapes[i] = Shell(shapes[i])
            elif type(shapes[i]) == TopoDS_Solid:
                shapes[i] = Solid(shapes[i])
            elif type(shapes[i]) == TopoDS_Compound:
                shapes[i] = Compound(shapes[i])
        return shapes

    def selected_shapes(self):
        """
        Get the selected shapes

        Returns:
            List[TopoDS_Shape]: List of selected shapes
        """
        shapes = self._display.GetSelectedShapes()
        shapes = self._convert_to_occwl_types(shapes)
        return shapes

    def show(self):
        """
        Show the viewer
        """
        self._start_display()

    def add_menu(self, name):
        """
        Add a custom menu to the viewer

        Args:
            name (str): Name of the menu
        """
        self._add_menu(name)

    def add_submenu(self, menu, callback):
        """
        Add a sub-menu to an existing menu

        Args:
            menu (str): Name of the menu
            callback (function): Function to be added as a sub-menu. The name of the function will appear under menu.
        """
        self._add_function_to_menu(menu, callback)

    def exit(self):
        """
        Exit the viewer
        """
        import sys

        sys.exit()

    def selection_mode_vertex(self):
        """
        Allow vertices to be selected
        """
        self._display.SetSelectionMode(TopAbs_VERTEX)

    def selection_mode_edge(self):
        """
        Allow edges to be selected
        """
        self._display.SetSelectionMode(TopAbs_EDGE)

    def selection_mode_face(self):
        """
        Allow faces to be selected
        """
        self._display.SetSelectionMode(TopAbs_FACE)

    def selection_mode_shell(self):
        """
        Allow all shapes to be selected
        """
        self._display.SetSelectionMode(TopAbs_SHELL)

    def selection_mode_solid(self):
        """
        Allow no shapes to be selected
        """
        self._display.SetSelectionMode(TopAbs_SOLID)

    def selection_mode_none(self):
        """
        Allow no shapes to be selected
        """
        self._display.SetSelectionModeShape()


class OffscreenRenderer(_BaseViewer):
    """
    Offscreen renderer that doesn't create a window. Useful for batch rendering.
    """
    def __init__(self, size: Optional[Tuple[int, int]] = (1024, 768),
        axes: Optional[bool] = True,
        background_top_color: Optional[List[int]] = [206, 215, 222],
        background_bottom_color: Optional[List[int]] = [128, 128, 128]
    ):
        """        
        Construct the OffscreenRenderer

        Args:
            size (Optional[Tuple[int, int]], optional): Size of the viewer window. Defaults to (1024, 768).
            axes (Optional[bool], optional): Show arrows for coordinate axes. Defaults to True.
            background_top_color (Optional[List[int]], optional): Background color at the top. Defaults to [206, 215, 222].
            background_bottom_color (Optional[List[int]], optional): Background color at the bottom. Defaults to [128, 128, 128].
        """
        super().__init__()
        self._display = Viewer3d()
        self._display.Create()
        if axes:
            self.show_axes()
        else:
            self.hide_axes()
        self.set_size(*size)
        self.set_background_color(background_top_color, background_bottom_color)
        self.shaded()
