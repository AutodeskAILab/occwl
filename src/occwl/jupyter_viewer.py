import numpy as np
import math 
from typing import Any, Callable, List, Optional, Tuple
from OCC.Core.TopoDS import TopoDS_Vertex, TopoDS_Edge, TopoDS_Face, TopoDS_Shell, TopoDS_Solid

from OCC.Display.WebGl.jupyter_renderer import JupyterRenderer

from matplotlib.cm import get_cmap
from matplotlib.colors import Normalize
from matplotlib.colors import rgb2hex
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from occwl.vertex import Vertex
from occwl.edge import Edge
from occwl.face import Face
from occwl.solid import Solid

class MultiSelectJupyterRenderer(JupyterRenderer):
    """
    This class derived from JupyterRenderer allows more than 
    one shape to be selected at a time.
    """

    def __init__(self, *args, **kwargs):
        super(MultiSelectJupyterRenderer, self).__init__(*args, **kwargs)
            
    def click(self, value):
        """ called whenever a shape  or edge is clicked
        """
        try:
            obj = value.owner.object
            self.clicked_obj = obj
            if self._current_mesh_selection != obj:
                if obj is not None:
                    self._shp_properties_button.disabled = False
                    self._toggle_shp_visibility_button.disabled = False
                    self._remove_shp_button.disabled = False
                    id_clicked = obj.name  # the mesh id clicked
                    self._current_mesh_selection = obj
                    self._current_selection_material_color = obj.material.color
                    obj.material.color = self._selection_color
                    # selected part becomes transparent
                    obj.material.transparent = True
                    obj.material.opacity = 0.5
                    # get the shape from this mesh id
                    selected_shape = self._shapes[id_clicked]
                    self._current_shape_selection = selected_shape
                # then execute calbacks
                for callback in self._select_callbacks:
                    callback(self._current_shape_selection)
        except Exception as e:
            self.html.value = f"{str(e)}"


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
        self._renderer = MultiSelectJupyterRenderer(
            size=size, 
            background_color=background_color
        )
        self._renderer.register_select_callback(self._select_callback)
        self._selected_faces = []
        self._selected_edges = []


    def display(
        self, 
        shape, 
        update=False, 
        shape_color=None, 
        render_edges=False,
        edge_color=None, 
        transparency=0.0
    ):
        """
        Display a shape (must be a Solid, Face, or Edge)

        Args:
            shape (Solid, Face, or Edge): Shape to display
            update (bool, optional): Whether to update and repaint. Defaults to False.
            shape_color ([type], optional): Color of the shape.
            edge_color ([type], optional):  Color of the shape's edges.
                                            Can be 'WHITE', 'BLUE', 'RED', 'GREEN', 'YELLOW',
                                            'CYAN', 'BLACK', 'ORANGE' or [r,g,b] 
                                            Defaults to None.
            render_edges (bool): Whether to render edges
        """
        if isinstance(shape, Solid):
            shape = shape.topods_solid()
        if isinstance(shape, Face):
            shape = shape.topods_face()
        if isinstance(shape, Edge):
            shape = shape.topods_edge()
        
        self._renderer.DisplayShape(
            shape, 
            update=update, 
            shape_color=shape_color,
            render_edges=render_edges,
            edge_color=edge_color
        )

    def display_face_colormap(
        self, 
        solid,
        values_for_faces,
        color_map = "rainbow",
        update=False, 
        render_edges=False,
        edge_color=None, 
    ):
        """
        Display a solid with the faces colored according to
        some scalar function.

        Args:
            solid (Solid,): Solid to display
            update (bool, optional): Whether to update and repaint. Defaults to False.
            color_map (str): Choose from https://matplotlib.org/stable/tutorials/colors/colormaps.html
            values_for_faces (list, np.array): Array of values, one for each face 
            render_edges (bool): Whether to render edges
        """
        if not isinstance(values_for_faces, np.ndarray):
            values_for_faces = np.array(values_for_faces)

        assert values_for_faces.size == solid.num_faces(), "Must have one value for each face"

        norm = Normalize(values_for_faces.min(), values_for_faces.max())
        norm_values_for_faces = norm(values_for_faces)

        color_mapper = get_cmap(color_map)
        face_colors = color_mapper(norm_values_for_faces)[:, :3]

        for face_index, face in enumerate(solid.faces()):
            shape_color=rgb2hex(face_colors[face_index])
            self.display(
                face, 
                update=False, 
                shape_color=shape_color, 
                render_edges=render_edges,
                edge_color=edge_color
            )

        # Plot the color scale
        ax = plt.subplot()
        color_mapper = get_cmap("rainbow")
        values = np.arange(100)
        values = np.stack([values]*5)
        im = ax.imshow(values, color_mapper)
        plt.tick_params(
            axis='both',       # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=False,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            left=False,        # ticks along the left edge are off
            labelbottom=False, # labels along the bottom edge are off
            labelleft=False    # labels along the left edge are off
        ) 
        plt.show()

        if update:
            self.show()


    def _select_callback(self, topo_ds_shape):
        """
        Callback called when a selection occurs
        """
        if type(topo_ds_shape) == TopoDS_Edge:
            self._selected_edges.append(Edge(topo_ds_shape))
        elif type(topo_ds_shape) == TopoDS_Face:
            self._selected_faces.append(Face(topo_ds_shape))
        

    def selected_faces(self):
        """
        Get the selected faces

        Returns:
            List[Face]: List of selected faces
        """
        return self._selected_faces


    def selected_face_indices(self, entity_mapper):
        """
        Get the selected face indices

        Returns:
           np.ndarray(int) : List of indices of selected faces
        """
        selected_face_indices = []
        for f in self._selected_faces:
            selected_face_indices.append(entity_mapper.face_index(f))
        return np.array(selected_face_indices)

    def selected_edges(self):
        """
        Get the selected edges

        Returns:
            List[Face]: List of selected edges
        """
        return self._selected_faces

    def selected_edge_indices(self, entity_mapper):
        """
        Get the selected edge indices

        Returns:
           np.ndarray(int) : List of indices of selected edges
        """
        selected_edge_indices = []
        for e in self._selected_edges:
            selected_edge_indices.append(entity_mapper.edge_index(e))
        return np.array(selected_edge_indices)


    def show(self):
        """
        Show the viewer
        """
        self._renderer.Display()