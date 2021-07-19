from datetime import datetime
from typing import Any, Callable, List, Optional, Tuple

from OCC.Core.AIS import (
    AIS_Shaded,
    AIS_Shape,
    AIS_Shape_SelectionMode,
    AIS_TexturedShape,
    AIS_WireFrame,
)
from OCC.Core.gp import gp_Pnt, gp_Pnt2d
from OCC.Display.SimpleGui import init_display
from OCC.Core.TopAbs import (
    TopAbs_VERTEX,
    TopAbs_EDGE,
    TopAbs_FACE,
    TopAbs_SHELL,
    TopAbs_SOLID,
)
from OCC.Core.TopoDS import (
    TopoDS_Vertex,
    TopoDS_Edge,
    TopoDS_Face,
    TopoDS_Shell,
    TopoDS_Solid,
)
from occwl.vertex import Vertex
from occwl.edge import Edge
from occwl.face import Face
from occwl.solid import Solid


class Viewer:
    """
    A Viewer for solid models
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

    def display(self, shape, update=False, color=None, transparency=0.0):
        """
        Display a shape (must be a Solid, Face, or Edge)

        Args:
            shape (Solid, Face, or Edge): Shape to display
            update (bool, optional): Whether to update and repaint. Defaults to False.
            color ([type], optional): Color of the shape.
                                      Can be 'WHITE', 'BLUE', 'RED', 'GREEN', 'YELLOW',
                                      'CYAN', 'BLACK', 'ORANGE'. Defaults to None.
            transparency (float, optional): How transparent the shape is. Defaults to 0.0.
        """
        if isinstance(shape, (Solid, Face, Edge, Vertex)):
            shape = shape.topods_shape()
        return self._display.DisplayShape(
            shape, update=update, color=color, transparency=transparency
        )

    def display_text(self, xyz, text, height=None, color=None):
        """
        Display a text

        Args:
            xyz (tuple of floats or 3D np.ndarray): Coordinate in model space where text would appear
            text (str): Text to display
            height (float, optional): Height of the text font. Defaults to None.
            color (tuple of 3 floats, optional): RGB color. Defaults to None.
        """
        return self._display.DisplayMessage(
            gp_Pnt(xyz[0], xyz[1], xyz[2]), text, height=height, message_color=color
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
