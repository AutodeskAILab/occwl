import numpy as np
import math
import sys
import uuid

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

# pythreejs
try:
    from pythreejs import (CombinedCamera, BufferAttribute, BufferGeometry, Mesh,
                           LineSegmentsGeometry, LineMaterial, LineSegments2, AmbientLight,
                           DirectionalLight, Scene, OrbitControls, Renderer,
                           Picker, Group, GridHelper, Line,
                           ShaderMaterial, ShaderLib, LineBasicMaterial,
                           PointsMaterial, Points, LineSegments, make_text)
except ImportError:
    print("pythreejs is not installed")
    sys.exit(0)

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

    def add_points(self, points_array, vertex_color="red", vertex_width=5, update=False):
        """ 
        Args:
            points_array (np.array): A numpy array of points [ num_points x 3 ]
            vertex_color (str): color for the points
            vertex_width (int): vertex width in pixels
            update (bool): Update the display
        """
        point_cloud_id = "%s" % uuid.uuid4().hex
        points_array = np.array(points_array, dtype=np.float32)
        attributes = {"position": BufferAttribute(points_array, normalized=False)}
        mat = PointsMaterial(color=vertex_color, sizeAttenuation=True, size=vertex_width)
        geom = BufferGeometry(attributes=attributes)
        points = Points(geometry=geom, material=mat, name=point_cloud_id)
        self._displayed_pickable_objects.add(points)

        if update:
            self.Display()

    def add_lines(self, start_arr, end_arr, line_color="blue", line_width=2, update=False):
        """ 
        Args:
            start_arr (np.array): A numpy array of points [ num_points x 3 ]
            end_arr (np.array): A numpy array of points [ num_points x 3 ]
            line_color (str): color for the points
            vertex_width (int): vertex width in pixels
            update (bool): Update the display
        """
        line_cloud_id = "%s" % uuid.uuid4().hex
        points = np.stack([start_arr, end_arr], axis=1)       
        points = np.array(points, dtype=np.float32)    
        geom = LineSegmentsGeometry(positions=points)
        mat = LineMaterial(linewidth=line_width, color=line_color)
        lines = LineSegments2(geom, mat, name=line_cloud_id)
        self._displayed_pickable_objects.add(lines)

        if update:
            self.Display()


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
            transparency (float, optional): Defaults to 0. (opaque). 0. is fully opaque, 1. is fully transparent.
        """
        shape = shape.topods_shape()
        
        self._renderer.DisplayShape(
            shape, 
            update=update, 
            shape_color=shape_color,
            render_edges=render_edges,
            edge_color=edge_color,
            transparency=transparency != 0.,
            opacity=1. - transparency
        )

    def display_face_colormap(
        self, 
        solid,
        values_for_faces,
        color_map = "rainbow",
        update=False, 
        render_edges=False,
        edge_color=None,
        transparency=0.
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
            transparency (float, optional): Defaults to 0. (opaque). 0. is fully opaque, 1. is fully transparent.
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
                edge_color=edge_color,
                transparency=transparency
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

    def display_points(
        self, 
        points, 
        normals=None, 
        point_color="red", 
        point_width=4,
        update=False
    ):
        """
        Display a set of points

        Args:
            points (np.array): Array of points size [ num_points x 3 ] 
        """
        self._renderer.add_points(
            points, 
            vertex_color=point_color, 
            vertex_width=point_width, 
            update=update
        )



    def display_lines(
        self, 
        start_points,
        end_points,
        line_color="blue", 
        line_width=1,
        update=False
    ):
        """
        Display points a set of points

        Args:
            start_points (np.array): Array of start_points size [ num_points x 3 ] 
            end_points (np.array): Array of end_points size [ num_points x 3 ] 
        """
        self._renderer.add_lines(
            start_points,
            end_points,
            line_color=line_color, 
            line_width=line_width, 
            update=update
        )


    def display_unit_vectors(
        self, 
        points,
        directions,
        line_color="blue", 
        line_width=2,
        update=False
    ):
        """
        Display a set of unit vectors

        Args:
            points (np.array): Array of points size [ num_points x 3 ] 
            directions (np.array): Array of directions size [ num_points x 3 ] 
        """
        mins = np.min(points, axis=0)
        maxs = np.max(points, axis=0)
        diag = maxs - mins
        longest = np.max(diag)
        line_length = longest/20
        end_points = points + directions*line_length
        self.display_lines(
                points,
                end_points,
                line_color=line_color, 
                line_width=line_width,
                update=False
            )


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