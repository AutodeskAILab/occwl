import numpy as np

from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pnt2d, gp_Ax2
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add, brepbndlib_AddOptimal
from OCC.Extend import TopologyUtils
from OCC.Core.BRepGProp import (
    brepgprop_LinearProperties,
    brepgprop_SurfaceProperties,
    brepgprop_VolumeProperties,
)
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.GProp import GProp_GProps
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax1, gp_Vec, gp_Trsf
from OCC.Core.ShapeUpgrade import ShapeUpgrade_ShapeDivideClosed
from OCC.Core.ShapeUpgrade import ShapeUpgrade_ShapeDivideClosedEdges
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform


class VertexContainerMixin:
    """
    A mixin class that adds the ability to perform operations on the vertices
    in the shape
    """
    def num_vertices(self):
        """
        Number of vertices in the Shape

        Returns:
            int: Number of vertices
        """
        return self._top_exp.number_of_vertices()

    def vertices(self):
        """
        Get an iterator to go over all vertices in the Shape

        Returns:
            Iterator[occwl.vertex.Vertex]: Vertex iterator
        """
        from occwl.vertex import Vertex
        return map(Vertex, self._top_exp.vertices())


class EdgeContainerMixin:
    """
    A mixin class that adds the ability to perform operations on the edges
    in the shape
    """
    def num_edges(self):
        """
        Number of edges in the Shape

        Returns:
            int: Number of edges
        """
        return self._top_exp.number_of_edges()

    def edges(self):
        """
        Get an iterator to go over all edges in the Shape

        Returns:
            Iterator[occwl.edge.Edge]: Edge iterator
        """
        from occwl.edge import Edge
        return map(Edge, self._top_exp.edges())
    
    def vertices_from_edge(self, edge):
        """
        Get an iterator to go over the vertices bounding an edge

        Args:
            edge (occwl.edge.Edge): Input edge

        Returns:
            Iterator[occwl.vertex.Vertex]: Vertex iterator
        """
        from occwl.vertex import Vertex
        from occwl.edge import Edge
        assert isinstance(edge, Edge)
        return map(Vertex, self._top_exp.vertices_from_edge(edge.topods_shape()))
    
    def find_closest_edge_slow(self, datum):
        """
        Find the closest edge to the given datum point.
        The function is for testing only.  It will be slow 
        as it loops over all edges in the Shape.
        A quick way to find the closest entity is to call
        Shape.find_closest_point_data(), but then you
        may get a face, edge or vertex back.
        
        Args:
            datum (np.ndarray or tuple): 3D datum point

        Returns:
            Face: The closest face in the Shape
        """
        return _find_closest_shape_in_list(self.edges(), datum)
    
    def split_all_closed_edges(self, max_tol=0.01, precision=0.01, num_splits=1):
        """
        Split all the closed edges in this shape

        Args:
            max_tol (float, optional): Maximum tolerance allowed. Defaults to 0.01.
            precision (float, optional): Precision of the tool when splitting. Defaults to 0.01.
            num_splits (int, optional): Number of splits to perform. Each split edge will result in num_splits + 1 edges. Defaults to 1.

        Returns:
            occwl.*.*: Shape with closed edges split
        """
        divider = ShapeUpgrade_ShapeDivideClosedEdges(self.topods_shape())
        divider.SetPrecision(precision)
        divider.SetMinTolerance(0.1 * max_tol)
        divider.SetMaxTolerance(max_tol)
        divider.SetNbSplitPoints(num_splits)
        ok = divider.Perform()
        if not ok:
            # Splitting failed or there were no closed edges to split
            # Return the original shape
            return self
        return type(self)(divider.Result())


class WireContainerMixin:
    """
    A mixin class that adds the ability to perform operations on the wires
    in the shape
    """
    def num_wires(self):
        """
        Number of wires in the Shape

        Returns:
            int: Number of wires
        """
        return self._top_exp.number_of_wires()

    def wires(self):
        """
        Get an iterator to go over all wires in the Shape

        Returns:
            Iterator[occwl.wire.Wire]: Wire iterator
        """
        from occwl.wire import Wire
        return map(Wire, self._top_exp.wires())


class FaceContainerMixin:
    """
    A mixin class that adds the ability to perform operations on the faces
    in the shape
    """
    def num_faces(self):
        """
        Number of faces in the Shape

        Returns:
            int: Number of faces
        """
        return self._top_exp.number_of_faces()

    def faces(self):
        """
        Get an iterator to go over all faces in the Shape

        Returns:
            Iterator[occwl.face.Face]: Face iterator
        """
        from occwl.face import Face
        return map(Face, self._top_exp.faces())

    def vertices_from_face(self, face):
        """
        Get an iterator to go over the vertices in a face

        Args:
            face (occwl.face.Face): Input face

        Returns:
            Iterator[occwl.vertex.Vertex]: Vertex iterator
        """
        from occwl.vertex import Vertex
        from occwl.face import Face
        assert isinstance(face, Face)
        return map(Vertex, self._top_exp.vertices_from_face(face.topods_shape()))

    def edges_from_face(self, face):
        """
        Get an iterator to go over the edges in a face

        Args:
            face (occwl.face.Face): Input face

        Returns:
            Iterator[occwl.edge.Edge]: Edge iterator
        """
        from occwl.edge import Edge
        from occwl.face import Face
        assert isinstance(face, Face)
        return map(Edge, self._top_exp.edges_from_face(face.topods_shape()))
    
    def wires_from_face(self, face):
        """
        Get an iterator to go over the wires bounding a face

        Args:
            face (occwl.face.Face): Input face

        Returns:
            Iterator[occwl.wire.Wire]: Wire iterator
        """
        from occwl.wire import Wire
        from occwl.face import Face
        assert isinstance(face, Face)
        return map(Wire, self._top_exp.wires_from_face(face.topods_shape()))
    
    def find_closest_face_slow(self, datum):
        """
        Find the closest face to the given datum point.
        The function is for testing only. It will be slow 
        as it loops over all faces in the Shape.
        A quick way to find the closest entity is to call
        Shape.find_closest_point_data(), but then you
        may get a face, edge or vertex back.
        
        Args:
            datum (np.ndarray or tuple): 3D datum point

        Returns:
            Face: The closest face in the Shape
        """
        return _find_closest_shape_in_list(self.faces(), datum)
    
    def split_all_closed_faces(self, max_tol=0.01, precision=0.01, num_splits=1):
        """
        Split all the closed faces in this shape

        Args:
            max_tol (float, optional): Maximum tolerance allowed. Defaults to 0.01.
            precision (float, optional): Precision of the tool when splitting. Defaults to 0.01.
            num_splits (int, optional): Number of splits to perform. Each split face will result in num_splits + 1 faces. Defaults to 1.

        Returns:
            occwl.*.*: Shape with closed faces split
        """
        divider = ShapeUpgrade_ShapeDivideClosed(self.topods_shape())
        divider.SetPrecision(precision)
        divider.SetMinTolerance(0.1 * max_tol)
        divider.SetMaxTolerance(max_tol)
        divider.SetNbSplitPoints(num_splits)
        ok = divider.Perform()
        if not ok:
            # Splitting failed or there were no closed faces to split
            # Return the original shape
            return self
        return type(self)(divider.Result())


class ShellContainerMixin:
    """
    A mixin class that adds the ability to perform operations on the shells
    in the shape
    """
    def num_shells(self):
        """
        Number of shells in the Shape

        Returns:
            int: Number of shells
        """
        return self._top_exp.number_of_shells()

    def shells(self):
        """
        Get an iterator to go over all shells in the Shape

        Returns:
            Iterator[occwl.shell.Shell]: Shell iterator
        """
        from occwl.shell import Shell
        return map(Shell, self._top_exp.shells())


class SolidContainerMixin:
    """
    A mixin class that adds the ability to perform operations on the solids
    in the shape
    """
    def num_solids(self):
        """
        Number of solids in the Compound

        Returns:
            int: Number of solids
        """
        return self._top_exp.number_of_solids()

    def solids(self):
        """
        Get an iterator to go over all solids in the Compound

        Returns:
            Iterator[occwl.solid.Solid]: Solid iterator
        """
        from occwl.solid import Solid
        return map(Solid, self._top_exp.solids())


class BottomUpFaceIterator:
    """
    A mixin class that adds the ability to iterate over faces from lower-level entities
    (vertices and edges).
    """
    def faces_from_edge(self, edge):
        """
        Get an iterator to go over the faces adjacent to an edge

        Args:
            edge (occwl.edge.Edge): Input edge

        Returns:
            Iterator[occwl.face.Face]: Face iterator
        """
        from occwl.edge import Edge
        from occwl.face import Face
        assert isinstance(edge, Edge)
        return map(Face, self._top_exp.faces_from_edge(edge.topods_shape()))

    def faces_from_vertex(self, vertex):
        """
        Get an iterator to go over the faces adjacent to a vertex

        Args:
            edge (occwl.vertex.Vertex): Input vertex

        Returns:
            Iterator[occwl.face.Face]: Face iterator
        """
        from occwl.vertex import Vertex
        from occwl.face import Face
        assert isinstance(vertex, Vertex)
        return map(Face, self._top_exp.faces_from_vertex(vertex.topods_shape()))
    
    def edge_continuity(self, edge):
        """
        Get the neighboring faces' continuity at given edge

        Args:
            edge (occwl.edge.Edge): Edge

        Returns:
            GeomAbs_Shape: enum describing the continuity order
        """
        faces = list(self.faces_from_edge(edge))
        # Handle seam edges which only have one face around them
        if len(faces) == 1:
            faces.append(faces[-1])
        return edge.continuity(faces[0], faces[1])



class BottomUpEdgeIterator:
    """
    A mixin class that adds the ability to iterate over edges from lower-level entities
    (vertices).
    """
    def edge_continuity(self, edge):
        """
        Get the neighboring faces' continuity at given edge

        Args:
            edge (occwl.edge.Edge): Edge

        Returns:
            GeomAbs_Shape: enum describing the continuity order
        """
        faces = list(self.faces_from_edge(edge))
        # Handle seam edges which only have one face around them
        if len(faces) == 1:
            faces.append(faces[-1])
        return edge.continuity(faces[0], faces[1])

    def edges_from_vertex(self, vertex):
        """
        Get an iterator to go over the edges adjacent to a vertex

        Args:
            face (occwl.face.Face): Input face

        Returns:
            Iterator[occwl.edge.Edge]: Edge iterator
        """
        from occwl.vertex import Vertex
        from occwl.edge import Edge
        assert isinstance(vertex, Vertex)
        return map(Edge, self._top_exp.edges_from_vertex(vertex.topods_shape()))


class TriangulatorMixin:
    """
    A mixin class that adds the ability to triangulate the faces that are present
    in the shape.
    """
    def triangulate_all_faces(
        self,
        triangle_face_tol=0.01,  # Tolerance between triangle and surface
        tol_relative_to_face=True,  # The tolerance value is relative to the face size
        angle_tol_rads=0.1,  # Angle between normals/tangents at triangle vertices
    ):
        return self.triangulate(
            triangle_face_tol=triangle_face_tol,
            tol_relative_to_face=tol_relative_to_face,
            angle_tol_rads=angle_tol_rads,
        )

    def triangulate(
        self,
        triangle_face_tol=0.01,  # Tolerance between triangle and surface
        tol_relative_to_face=True,  # The tolerance value is relative to the face size
        angle_tol_rads=0.1,  # Angle between normals/tangents at triangle vertices
    ):
        """
        Triangulate all the faces in the shape. You can then get the triangles 
        from each face separately using face.get_triangles().
        If you wanted triangles for the entire shape then call
        shape.get_triangles() below.
        For more details see 
        https://old.opencascade.com/doc/occt-7.1.0/overview/html/occt_user_guides__modeling_algos.html#occt_modalg_11
        
        Args:
            triangle_face_tol (float, optional): Tolerance between triangle and surface. Defaults to 0.01.
            tol_relative_to_face (bool): Whether tolerance is relative to face size
            angle_tol_rads (float, optional): Angle tolerance in radians. Defaults to 0.1.

        Returns:
            bool: Is successful
        """
        mesh = BRepMesh_IncrementalMesh(
            self.topods_shape(),
            triangle_face_tol,
            tol_relative_to_face,
            angle_tol_rads,
            True,
        )
        mesh.Perform()
        return mesh.IsDone()

    def get_triangles(
        self,
        triangle_face_tol=0.01,  # Tolerance between triangle and surface
        tol_relative_to_face=True,  # The tolerance value is relative to the face size
        angle_tol_rads=0.1,  # Angle between normals/tangents at triangle vertices
    ):
        """
        Compute and get the tessellation of the entire shape

        Args:
            triangle_face_tol (float, optional): Toelrance between triangle and surface. Defaults to 0.01.
            tol_relative_to_face (bool): Whether tolerance is relative to face size
            angle_tol_rads (float, optional): Angle tolerance in radians. Defaults to 0.1.

        Returns:
            2D np.ndarray (float): Vertices or None if triangulation failed
            2D np.ndarray (int): Faces or None if triangulation failed
        """
        ok = self.triangulate_all_faces(
            triangle_face_tol, tol_relative_to_face, angle_tol_rads
        )
        if not ok:
            # Failed to triangulate
            return None, None
        verts = []
        tris = []
        faces = self.faces()
        last_vert_index = 0
        for face in faces:
            fverts, ftris = face.get_triangles()
            verts.extend(fverts)
            for tri in ftris:
                new_indices = [index + last_vert_index for index in tri]
                tris.append(new_indices)
            last_vert_index = len(verts)
        return np.asarray(verts, dtype=np.float32), np.asarray(tris, dtype=np.int32)


class SurfacePropertiesMixin:
    """
    A mixin class that adds the ability to query surface properties (e.g. area).
    """
    def area(self):
        """
        Compute the area of the Shape

        Returns:
            float: Area
        """
        geometry_properties = GProp_GProps()
        brepgprop_SurfaceProperties(self.topods_shape(), geometry_properties)
        return geometry_properties.Mass()


class VolumePropertiesMixin:
    """
    A mixin class that adds the ability to query volumetric properties (e.g. volume, center of mass, etc.).
    """
    def volume(self, tolerance=1e-9):
        """
        Compute the volume of the Shape

        Args:
            tolerance (float, optional): Tolerance. Defaults to 1e-9.

        Returns:
            float: Volume
        """
        props = GProp_GProps()
        brepgprop_VolumeProperties(self.topods_shape(), props, tolerance)
        return props.Mass()

    def center_of_mass(self, tolerance=1e-9):
        """
        Compute the center of mass of the Shape

        Args:
            tolerance (float, optional): Tolerance. Defaults to 1e-9.

        Returns:
            np.ndarray: 3D point
        """
        from occwl.geometry import geom_utils
        props = GProp_GProps()
        brepgprop_VolumeProperties(self.topods_shape(), props, tolerance)
        com = props.CentreOfMass()
        return geom_utils.gp_to_numpy(com)

    def moment_of_inertia(self, point, direction, tolerance=1e-9):
        """
        Compute the moment of inertia about an axis

        Args:
            point (np.ndarray): 3D point (origin of the axis)
            direction (np.ndarray): 3D direction of the axis
            tolerance (float, optional): Tolerance. Defaults to 1e-9.

        Returns:
            float: Moment of inertia
        """
        from occwl.geometry import geom_utils
        props = GProp_GProps()
        brepgprop_VolumeProperties(self.topods_shape(), props, tolerance)
        axis = gp_Ax1(
            geom_utils.numpy_to_gp(point), geom_utils.numpy_to_gp_dir(direction)
        )
        return props.MomentOfInertia(axis)


class BoundingBoxMixin:
    """
    A mixin class that adds the ability to compute approximate and exact bounding box
    of the Shape.
    """
    def box(self):
        """
        Get a quick bounding box of the Shape

        Returns:
            Box: Bounding box
        """
        from occwl.geometry import geom_utils
        b = Bnd_Box()
        brepbndlib_Add(self.topods_shape(), b)
        return geom_utils.box_to_geometry(b)

    def exact_box(self, use_shapetolerance=False):
        """
        Get a slow, but accurate box for the Shape.

        Args:
            use_shapetolerance (bool, optional) Include the tolerance of edges
                                                and vertices in the box.

        Returns:
            Box: Bounding box
        """
        from occwl.geometry import geom_utils
        b = Bnd_Box()
        use_triangulation = True
        brepbndlib_AddOptimal(self.topods_shape(), b, use_triangulation, use_shapetolerance)
        return geom_utils.box_to_geometry(b)

    def scale_to_box(self, box_side, copy=True):
        """
        Translate and scale the Shape so it fits exactly 
        into the [-box_side, box_side]^3 box

        Args:
            box_side (float) The side length of the box
            copy (bool)      True - Copy entities and apply the transform to
                                    the underlying geometry
                             False - Apply the transform to the topods Locator
                                     if possible 

        Returns:
            occwl.*.*: The scaled version of this Shape
        """
        from occwl.geometry import geom_utils
        # Get an exact box for the Shape
        box = self.exact_box()
        center = box.center()
        longest_length = box.max_box_length()

        orig = gp_Pnt(0.0, 0.0, 0.0)
        center = geom_utils.numpy_to_gp(center)
        vec_center_to_orig = gp_Vec(center, orig)
        move_to_center = gp_Trsf()
        move_to_center.SetTranslation(vec_center_to_orig)

        scale_trsf = gp_Trsf()
        scale_trsf.SetScale(orig, (2.0 * box_side) / longest_length)
        trsf_to_apply = scale_trsf.Multiplied(move_to_center)
        
        return self._apply_transform(trsf_to_apply, copy=copy)


    def scale_to_unit_box(self, copy=True):
        """
        Translate and scale the Shape so it fits exactly 
        into the [-1, 1]^3 box

        Args:
            copy (bool)      True - Copy entities and apply the transform to
                                        the underlying geometry
                                False - Apply the transform to the topods Locator
                                        if possible 
        Returns:
            The scaled version of this shape
        """
        return self.scale_to_box(1.0, copy=copy)




def _find_closest_shape_in_list(shapes, datum):
    """
    In this function we search all shapes in the list 
    and return the closest one.   
    Typically you would want to find the closest entity 
    which may be a face, edge or vertex.  For this you can
    use Shape.find_closest_point_data()
    """
    closest_dist_yet = np.inf
    closest_shape = None
    for s in shapes:
        closest_point_data = s.find_closest_point_data(datum)
        if closest_point_data.distance < closest_dist_yet:
            closest_shape = s
            closest_dist_yet = closest_point_data.distance
    return closest_shape
