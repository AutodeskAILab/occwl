from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Extend.DataExchange import read_step_file
from OCC.Extend.TopologyUtils import list_of_shapes_to_compound
from OCC.Core.BRepTools import BRepTools_ShapeSet
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.TopAbs import (
    TopAbs_FACE, 
    TopAbs_EDGE, 
    TopAbs_SHELL, 
    TopAbs_SOLID, 
    TopAbs_COMPOUND, 
    TopAbs_COMPSOLID
)
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.StepRepr import StepRepr_RepresentationItem

from occwl.base import BottomUpFaceIterator, BottomUpEdgeIterator, BoundingBoxMixin, \
    EdgeContainerMixin, FaceContainerMixin, SolidContainerMixin, SurfacePropertiesMixin, \
        TriangulatorMixin, VertexContainerMixin, VolumePropertiesMixin, WireContainerMixin, \
            ShellContainerMixin
from occwl.shape import Shape


class Compound(Shape, BottomUpFaceIterator, BoundingBoxMixin, BottomUpEdgeIterator,
    EdgeContainerMixin, FaceContainerMixin, SolidContainerMixin, ShellContainerMixin, SurfacePropertiesMixin,
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

    @staticmethod
    def load_step_with_attributes(step_filename):
        """Load shapes from a step file with the
        name information.   Other attributes could be
        retro-fitted

        Args:
            step_filename (str): Path to STEP file

        Returns:
            occwl.Compound, dict occwl.Shape to attributes 
        """        
        # Read the file and get the shape
        reader = STEPControl_Reader()
        tr = reader.WS().TransferReader()
        reader.ReadFile(str(step_filename))
        reader.TransferRoots()
        shape = reader.OneShape()
            
        occwl_shape_to_attributes = {}
        def check_shape_type(shape_type):
            exp = TopExp_Explorer(shape, shape_type)
            while exp.More():
                s = exp.Current()
                exp.Next()
                item = tr.EntityFromShapeResult(s, 1)
                if item is None:
                    continue
                item = StepRepr_RepresentationItem.DownCast(item)
                if item is None:
                    continue
                name = item.Name().ToCString()
                occwl_shape = Shape.occwl_shape(s)
                occwl_shape_to_attributes[occwl_shape] = {
                    "name": name
                }

        check_shape_type(TopAbs_FACE)
        check_shape_type(TopAbs_EDGE)
        check_shape_type(TopAbs_SHELL)
        check_shape_type(TopAbs_SOLID)
        check_shape_type(TopAbs_COMPOUND)
        check_shape_type(TopAbs_COMPSOLID)

        shp, success = list_of_shapes_to_compound([shape])
        assert success, "Failed to convert to a single compound"
        return Compound(shp), occwl_shape_to_attributes


    @staticmethod
    def load_from_occ_native(filename, verbosity=False):
        """
        Load everything from the OCC native .brep file 
        format into a single occwl.compound.Compound.

        Note:  Saving to and loading from the native file format 
               is between one and two orders of magnitude faster 
               than loading from STEP, so it is recommended for 
               large scale data processing

        Args:
            filename (str or pathlib.Path): .brep filename
            verbosity (bool): Whether to print detailed information while loading

        Returns:
            occwl.compound.Compound: Compound shape
        """
        shape_set = BRepTools_ShapeSet()
        with open(filename, "r") as fp:
            shape_set.ReadFromString(fp.read())
        shapes = []
        for i in range(shape_set.NbShapes()):
            shapes.append(shape_set.Shape(i+1))
        shp, success = list_of_shapes_to_compound(shapes)
        assert success
        return Compound(shp)