from OCC.Core.STEPControl import STEPControl_Reader
from occwl.solid import Solid
from OCC.Extend.DataExchange import export_shape_to_svg
from OCC.Extend import TopologyUtils


def load_step(step_filename):
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


def save_svg(shape,
             filename,
             export_hidden_edges=True,
             location=(0, 0, 0),
             direction=(1, 1, 1),
             color="black",
             line_width=0.1):
    
    svg_string = export_shape_to_svg(shape, filename=filename, export_hidden_edges=export_hidden_edges,
                                     location=gp_Pnt(*location), direction=gp_Dir(*direction),
                                     color=color, line_width=line_width,
                                     margin_left=0, margin_top=0)


def save_stl(shape, filename, binary=True):
    from OCC.Extend.DataExchange import write_stl_file
    write_stl_file(shape,
                   filename,
                   mode="binary" if binary else "ascii")
