import numpy as np
import math 
from OCC.Display.WebGl.jupyter_renderer import JupyterRenderer

class JupyterViewer:
    """
    A viewer for models in a Jupyter notebook
    """
       
    def __init__(
        self,
        size: Optional[Tuple[int, int]] = (640, 480),
        background_color: Optional[str] ="white"
    ):
        """
        Construct the Viewer

        Args:
        """
        self._renderer = JupyterRenderer(
            size=size, 
            background_color=background_color
        )
        self._renderer.register_select_callback(self._select_callback)
        self._selected_shapes = []


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
        assert 0.0 <= transparency, "Transparency should be in range 0-1"
        assert transparency <= 1.0, "Transparency should be in range 0-1"

        opacity = 1.0 - transparency

        shape_color = None
        edge_color = None
        if isinstance(shape, Solid):
            shape_color = color
            shape = shape.topods_solid()
        if isinstance(shape, Face):
            shape_color = color
            shape = shape.topods_face()
        if isinstance(shape, Edge):
            edge_color = color
            shape = shape.topods_edge()
        
        self.renderer.DisplayShape(
            shape, 
            update=update, 
            shape_color=shape_color, 
            edge_color=edge_color
        )


    def _select_callback(self, topo_ds_shape):
        if type(topo_ds_shape) == TopoDS_Vertex:
            self._selected_shapes.append(Vertex(topo_ds_shape))
        elif type(shapes[i]) == TopoDS_Edge:
            self._selected_shapes.append(Edge(topo_ds_shape))
        elif type(shapes[i]) == TopoDS_Face:
            self._selected_shapes.append(Face(topo_ds_shape))
        
    def selected_shapes(self):
        """
        Get the selected shapes

        Returns:
            List[TopoDS_Shape]: List of selected shapes
        """
        return self._selected_shapes

    def show(self):
        """
        Show the viewer
        """
        self.self._renderer.Display()