"""
Base class for faces, edges and vertices
"""
import numpy as np
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape
from OCC.Core.BRepTools import BRepTools_ShapeSet
from OCC.Core.Extrema import Extrema_ExtFlag_MIN
from OCC.Core.Message import Message_ProgressRange
from OCC.Core.gp import gp_Ax1, gp_Trsf
from OCC.Core.TopAbs import TopAbs_REVERSED
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TopoDS import (
    TopoDS_Edge,
    TopoDS_Face,
    TopoDS_Shell,
    TopoDS_Solid,
    TopoDS_Vertex,
    TopoDS_Wire,
    TopoDS_Compound,
    TopoDS_CompSolid,
)
from OCC.Extend.ShapeFactory import (
    rotate_shape,
    rotate_shp_3_axis,
    scale_shape,
    translate_shp,
)
from OCC.Core.BRepCheck import BRepCheck_Analyzer
from OCC.Extend import TopologyUtils
import occwl.geometry.geom_utils as geom_utils

class ClosestPointData:
    """
    A class to record information about the closest point on a shape
    to some datum point
    """

    def __init__(self, dist_shape_shape):
        """
        Args:
            dist_shape_shape (BRepExtrema_DistShapeShape): OCC class for distance to a shape
        """
        assert dist_shape_shape.IsDone()
        self.closest_entity = dist_shape_shape.SupportOnShape2(1)
        self.closest_point = geom_utils.gp_to_numpy(dist_shape_shape.PointOnShape2(1))
        self.distance = dist_shape_shape.Value()


class Shape:
    def __init__(self, topods_shape):
        """
        Construct the Shape (this class is not meant to be instantiated directly)

        Args:
            topods_shape (OCC.Core.TopoDS.TopoDS_Vertex/Edge/Face/Wire/Shell/Solid): OCC TopoDS_* as provided by the derived class

        Raises:
            Exception: [description]
        """
        if type(self) == Shape:
            raise Exception("Shape must be subclassed and instantiated.")
        assert isinstance(
            topods_shape,
            (
                TopoDS_Vertex,
                TopoDS_Edge,
                TopoDS_Face,
                TopoDS_Wire,
                TopoDS_Shell,
                TopoDS_Solid,
                TopoDS_Compound,
                TopoDS_CompSolid,
            ),
        )
        self._shape = topods_shape
        self._top_exp = TopologyUtils.TopologyExplorer(self.topods_shape(), True)

    def topods_shape(self):
        """
        Get the underlying OCC shape

        Returns:
            OCC.Core.TopoDS.TopoDS_Vertex/Edge/Face/Wire/Shell/Solid: OCC TopoDS_*
        """
        return self._shape

    @staticmethod
    def occwl_shape(topods_shape):
        """
        Static method to create an occwl shape of the appropriate 
        class from the given topods_shape
        Args:
            topods_shape (OCC.Core.TopoDS.TopoDS_Vertex/Edge/Face/Wire/Shell/Solid): TopoDS shape

        Returns:
            One of
                occwl.compound.Compound
                occwl.solid.Solid
                occwl.face.Face
                occwl.edge.Edge
                occwl.vertex.Vertex
                occwl.wire.Wire
                occwl.shell.Shell
        Raises:
            Exception: [description]
        """
        from occwl.compound import Compound
        from occwl.solid import Solid
        from occwl.face import Face
        from occwl.edge import Edge
        from occwl.vertex import Vertex
        from occwl.wire import Wire
        from occwl.shell import Shell

        if isinstance(topods_shape, TopoDS_Vertex):
            return Vertex(topods_shape)
        if isinstance(topods_shape, TopoDS_Edge):
            return Edge(topods_shape)
        if isinstance(topods_shape, TopoDS_Face):
            return Face(topods_shape)
        if isinstance(topods_shape, TopoDS_Wire):
            return Wire(topods_shape)
        if isinstance(topods_shape, TopoDS_Shell):
            return Shell(topods_shape)
        if isinstance(topods_shape, TopoDS_Solid):
            return Solid(topods_shape)
        if isinstance(topods_shape, (TopoDS_Compound, TopoDS_CompSolid)):
            return Compound(topods_shape)
        raise Exception(
            "Shape must be one of TopoDS_Vertex, TopoDS_Edge, TopoDS_Face, TopoDS_Shell, TopoDS_Solid, TopoDS_Compound, TopoDS_CompSolid"
        )

    def __hash__(self):
        """
        Hash for the shape

        Returns:
            int: Hash value
        """
        return self.topods_shape().__hash__()

    def __eq__(self, other):
        """
        Equality check for the shape

        NOTE: This function only checks if the shape is the same.
        It doesn't check the edge orienation for example, so 
        
        edge1 == edge2

        does not necessarily mean 

        edge1.reversed() == edge2.reversed()
        """
        return self.topods_shape().__hash__() == other.topods_shape().__hash__()

    def save_to_occ_native(
            self, 
            filename, 
            verbosity=False,
            with_triangles=False,
            with_normals=False,
            format_version=None
        ):
        """
        Save this shape into a native OCC binary .brep file.

        Note:  Saving to and loading from the native file format 
               is between one and two orders of magnitude faster 
               than loading from STEP, so it is recommended for 
               large scale data processing

        Args:
            filename (str or pathlib.Path): .brep filename
            with_triangles (bool): Whether to save triangle data cached in the shape.
            with_normals (bool): Whether to save vertex normals cached in the shape
            format_version (int):  Use None to save to the latest version
                1 - first revision
                2 - added storing of CurveOnSurface UV Points
                3 - [OCCT 7.6] added storing of per-vertex normal information
                               and dropped storing of CurveOnSurface UV Points
        """
        self.save_shapes_to_occ_native(
            filename, 
            [ self ],
            with_triangles=with_triangles,
            with_normals=with_normals,
            format_version=format_version
        )
    
    @staticmethod
    def save_shapes_to_occ_native(
            filename, 
            shapes,
            with_triangles=False,
            with_normals=False,
            format_version=None
        ):
        """
        Save this shape into a native OCC binary .brep file.

        Note:  Saving to and loading from the native file format 
                is between one and two orders of magnitude faster 
                than loading from STEP, so it is recommended for 
                large scale data processing

        Args:
            filename (str or pathlib.Path): .brep filename

            with_triangles (bool): Whether to save triangle data cached in the shape.
            with_normals (bool): Whether to save vertex normals cached in the shape
            format_version (int):  Use None to save to the latest version
                1 - first revision
                2 - added storing of CurveOnSurface UV Points
                3 - [OCCT 7.6] added storing of per-vertex normal information
                               and dropped storing of CurveOnSurface UV Points
        """
        new_api = False
        shapes_set = BRepTools_ShapeSet(with_triangles)
        # shapes_set.SetWithNormals(with_normals) # Not in OCC 7.5.0

        for shp in shapes:
            shapes_set.Add(shp.topods_shape())
        if format_version is not None:
            shapes_set.SetFormatNb(format_version)


        with open(filename, "w") as fp:
            s = shapes_set.WriteToString()
            fp.write(s)



    def reversed(self):
        """
        Whether this shape is reversed.
        
        - For an edge this is whether the edge is reversed with respect to the curve geometry
        - For a face this is whether the face is reversed with respect to the surface geometry
        - For a vertex this is whether the vertex is at the upper or lower parameter value on the
          edges curve

        Returns:
            bool: If rational
        """
        return self.topods_shape().Orientation() == TopAbs_REVERSED


    def find_closest_point_data(self, datum):
        """
        Find the information about the closest point on this shape
        
        Args:
            datum (np.ndarray): 3D Point
        
        Returns:
            ClosestPointData: Data about the closest point on this shape
            None: if error
        """
        # Folowing https://dev.opencascade.org/content/how-retrieve-nearest-face-shape-given-gppnt
        # Create a vertex from the point
        occ_point = geom_utils.numpy_to_gp(datum)
        vertex_maker = BRepBuilderAPI_MakeVertex(occ_point)
        vertex = vertex_maker.Shape()
        dist_shape_shape = BRepExtrema_DistShapeShape(
            vertex, self.topods_shape(), Extrema_ExtFlag_MIN
        )
        ok = dist_shape_shape.Perform()
        if not ok:
            return None

        return ClosestPointData(dist_shape_shape)

    def translate(self, offset):
        """
        Translate the shape by an offset vector

        Args:
            offset (np.ndarray): Offset vector
        """
        self._shape = translate_shp(self._shape, geom_utils.numpy_to_gp_vec(offset))

    def rotate_axis_angle(
        self, axis, angle_radians, origin=np.zeros(3, dtype=np.float32)
    ):
        """
        Rotate the shape about the given axis by the given angle in radians

        Args:
            axis (np.ndarray): Rotation axis
            angle_radians (float): Angle in radians
        """
        self._shape = rotate_shape(
            self._shape,
            gp_Ax1(geom_utils.numpy_to_gp(origin), geom_utils.numpy_to_gp_dir(axis)),
            angle_radians,
            unite="rad",
        )

    def rotate_euler_angles(self, angles_xyz_radians):
        """
        Rotate the shape by the given Euler angles in radians

        Args:
            angle_xyz_radians (np.ndarray): 3D array with angles to rotate about x-axis, y-axis and z-axis respectively in radians
        """
        self._shape = rotate_shp_3_axis(
            self._shape,
            angles_xyz_radians[0],
            angles_xyz_radians[1],
            angles_xyz_radians[2],
            unity="rad",
        )

    def scale(self, scale_vector):
        """
        Scale the shape by the given 3D vector

        Args:
            scale_vector (np.ndarray): 3D array with scales to resize the shape along the x-axis, y-axis and z-axis respectively
        """
        self._shape = scale_shape(
            self._shape, scale_vector[0], scale_vector[1], scale_vector[2]
        )

    def valid(self, return_analyzer=False):
        """
        Check if the shape is valid

        Args:
            return_analyzer (bool): Whether to return the BRepCheck_Analyzer object for more inspection

        Returns:
            bool: Whether the shape is valid
            BRepCheck_Analyzer [optional]: if return_analyzer is True
        """
        analyzer = BRepCheck_Analyzer(self.topods_shape())
        if return_analyzer:
            return analyzer.IsValid(), analyzer
        return analyzer.IsValid()



    def set_transform_to_identity(self):
        """
        When an assembly is loaded from a STEP file
        the solids will be transformed relative to
        their local coordinate system.   i.e. they
        are placed in the assembly root components 
        coordinate system.

        When working with individual bodies you often
        want them to be axis aligned, in which case 
        you want to remove the assembly transform.
        This function removes it for you.

        If however you want to bake the transform
        into the bodies and suppress the asserts 
        from parts of occwl which don't cope with
        transforms then use the transform() function
        below with copy=True
        """
        identity = TopLoc_Location()
        self.topods_shape().Location(identity)
        self._top_exp = TopologyUtils.TopologyExplorer(self.topods_shape(), True)
        self.convert_geometric_identity_transforms_to_identity()


    def convert_geometric_identity_transforms_to_identity(self):
        """
        Open Cascade models sometimes contain transforms which
        are "geometrically" identify transforms, but the identity
        flag is not set.

        This function checks each transform and sets the flag if 
        the appropriate.
        """
        identity = TopLoc_Location()
        if geom_utils.is_geometric_identity(
            self.topods_shape().Location().Transformation()
        ):
            self.topods_shape().Location(identity)
            self._top_exp = TopologyUtils.TopologyExplorer(self.topods_shape(), True)

        for face in self._top_exp.faces():
            if geom_utils.is_geometric_identity(face.Location().Transformation()):
                face.Location(identity)

        for edge in self._top_exp.edges():
            if geom_utils.is_geometric_identity(edge.Location().Transformation()):
                edge.Location(identity)

        for vertex in self._top_exp.vertices():
            if geom_utils.is_geometric_identity(vertex.Location().Transformation()):
                vertex.Location(identity)
        

    def transform(self, a: np.ndarray, copy=True):
        """
        Apply the given 3x4 transform matrix to the solid.

        Args: a (nd.array) - Homogeneous transform matrix
                             The transform that will be applied is
                                        
                             x' =  a[0,0]*x + a[0,1]*y + a[0,2]*z + a[0, 3]
                             y' =  a[1,0]*x + a[1,1]*y + a[1,2]*z + a[1, 3]
                             z' =  a[2,0]*x + a[2,1]*y + a[2,2]*z + a[2, 3]

             copy (bool)    True - Copy entities and apply the transform to
                                   the underlying geometry
                            False - Apply the transform to the topods Locator
                                    if possible 
        """
        assert (a.shape == (3, 4)), "Transform matrix must be 3x4"
        a = a.astype(np.float64)

        # Create an identity transform
        trsf = gp_Trsf()

        # If the matrix is an identity matrix then
        # we don't want to set the values as this
        # would give us a geometric identity without
        # the identity flag set
        if not np.allclose(a, np.eye(3, 4)):
            trsf.SetValues(
                a[0,0], a[0,1], a[0,2], a[0, 3],
                a[1,0], a[1,1], a[1,2], a[1, 3],
                a[2,0], a[2,1], a[2,2], a[2, 3]
            )
        return self._apply_transform(trsf, copy=copy)

    def _apply_transform(self, trsf_to_apply, copy=True):
        """
        Apply the given transform to this Shape
        """
        apply_transform = BRepBuilderAPI_Transform(trsf_to_apply)
        apply_transform.Perform(self.topods_shape(), copy)
        transformed_shape = apply_transform.ModifiedShape(self.topods_shape())

        return type(self)(transformed_shape)