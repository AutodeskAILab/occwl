from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Extend.DataExchange import read_step_file, list_of_shapes_to_compound
from occwl.base import BottomUpFaceIterator, BoundingBoxMixin, ClosedEntitySplitterMixin, \
    EdgeContainerMixin, FaceContainerMixin, SolidContainerMixin, SurfacePropertiesMixin, \
        TriangulatorMixin, VertexContainerMixin, VolumePropertiesMixin, WireContainerMixin
from occwl.shape import Shape


class Compound(Shape, BottomUpFaceIterator, BoundingBoxMixin, ClosedEntitySplitterMixin,
    EdgeContainerMixin, FaceContainerMixin, SolidContainerMixin, SurfacePropertiesMixin,
    TriangulatorMixin, VertexContainerMixin, VolumePropertiesMixin, WireContainerMixin):
    """
    A compound which can be worked with as many shapes
    lumped together.
    """
    def __init__(self, shape):
        assert isinstance(shape, TopoDS_Compound)
        super().__init__(shape)
    
    @staticmethod
    def load_from_step(filename, verbosity=False):
        """
        Load everything from a STEP file as a single Compound

        Args:
            filename (str or pathlib.Path): STEP filename
            verbosity (bool): Whether to print detailed information while loading

        Returns:
            occwl.compound.Compound: Compound shape
        """
        shp = read_step_file(str(filename), as_compound=True, verbosity=verbosity)
        if not isinstance(shp, TopoDS_Compound):
            shp, success = list_of_shapes_to_compound([shp])
            assert success
        return Compound(shp)
