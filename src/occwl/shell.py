from OCC.Core.TopoDS import TopoDS_Shell
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Sewing
from occwl.base import BottomUpEdgeIterator, BottomUpFaceIterator, BoundingBoxMixin, \
    EdgeContainerMixin, FaceContainerMixin, SurfacePropertiesMixin, \
        TriangulatorMixin, VertexContainerMixin, WireContainerMixin
from occwl.shape import Shape
from occwl.face import Face


class Shell(BottomUpFaceIterator, BottomUpEdgeIterator,
    BoundingBoxMixin,  VertexContainerMixin, EdgeContainerMixin, WireContainerMixin, FaceContainerMixin,
    SurfacePropertiesMixin, TriangulatorMixin, Shape):
    """
    A shell is a sewed set of faces.
    """
    def __init__(self, shape):
        assert isinstance(shape, TopoDS_Shell)
        super().__init__(shape)

    @staticmethod
    def make_by_sewing_faces(faces):
        """
        Make a shell by sewing a set of faces with overlapping edges

        Args:
            faces (List[occwl.face.Face]): List of faces

        Returns:
            Shell or None: Sewed shell or None if the output was not a Shell
        """
        sew = BRepBuilderAPI_Sewing()
        for f in faces:
            assert isinstance(f, Face)
            sew.Add(f.topods_shape())
        sew.Perform()
        sewed_shape = sew.SewedShape()
        if isinstance(sewed_shape, TopoDS_Shell):
            return Shell(sewed_shape)
        return None
