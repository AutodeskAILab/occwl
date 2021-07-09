from OCC.Core.STEPControl import STEPControl_Reader
from occwl.solid import Solid
from occwl.face import Face
from occwl.edge import Edge
from occwl.geometry import geom_utils
from OCC.Extend.DataExchange import export_shape_to_svg
from OCC.Extend import TopologyUtils
from OCC.Core.gp import gp_Pnt, gp_Dir


def load_step(step_filename):
    """Load solids from a STEP file

    Args:
        step_filename (str): Path to STEP file

    Returns:
        List of occwl.Solid: a list of solid models from the file
    """
    step_filename_str = str(step_filename)
    reader = STEPControl_Reader()
    reader.ReadFile(step_filename_str)
    reader.TransferRoots()
    shape = reader.OneShape()
    exp = TopologyUtils.TopologyExplorer(shape, True)
    bodies = []
    for body in exp.solids():
        bodies.append(Solid(body))
    return bodies


def save_svg(
    shape,
    filename,
    export_hidden_edges=True,
    location=(0, 0, 0),
    direction=(1, 1, 1),
    color="black",
    line_width=0.1,
):
    """Saves the shape outline as an SVG file

    Args:
        shape (Any occwl topology type): Any topological entity
        filename (str): Path to output SVG
        export_hidden_edges (bool, optional): Whether to render hidden edges as dotted lines in the SVG. Defaults to True.
        location (tuple, optional): Location. Defaults to (0, 0, 0).
        direction (tuple, optional): Direction. Defaults to (1, 1, 1).
        color (str, optional): Color of the paths in SVG. Defaults to "black".
        line_width (float, optional): Width of each path. Defaults to 0.1.
    """
    if isinstance(shape, Solid):
        shape = shape.topods_solid()
    elif isinstance(shape, Face):
        shape = shape.topods_face()
    elif isinstance(shape, Edge):
        shape = shape.topods_edge()
    else:
        raise NotImplementedError
    svg_string = export_shape_to_svg(
        shape,
        filename=filename,
        export_hidden_edges=export_hidden_edges,
        location=gp_Pnt(*location),
        direction=gp_Dir(*direction),
        color=color,
        line_width=line_width,
        margin_left=0,
        margin_top=0,
    )


def save_stl(shape, filename, binary=True):
    """Saves a tesselated entity as a STL file
    NOTE: Call Solid.triangulate_all_faces() first

    Args:
        shape ([type]): [description]
        filename ([type]): [description]
        binary (bool, optional): [description]. Defaults to True.
    """
    from OCC.Extend.DataExchange import write_stl_file

    write_stl_file(shape, filename, mode="binary" if binary else "ascii")
