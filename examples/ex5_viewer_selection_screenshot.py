import pathlib
from occwl.edge import Edge
from occwl.face import Face
from occwl.solid import Solid
from occwl.vertex import Vertex
from occwl.viewer import Viewer
from occwl.compound import Compound

v = Viewer(backend="wx")


def select_vertex(event=None):
    v.selection_mode_none()
    v.selection_mode_vertex()


def select_edge(event=None):
    v.selection_mode_none()
    v.selection_mode_edge()


def select_face(event=None):
    v.selection_mode_none()
    v.selection_mode_face()


def dump(event=None):
    filename = pathlib.Path(__file__).resolve().parent.joinpath("screenshot.png")
    v.save_image(filename)


# Add menu for selection mode
v.add_menu("select")
v.add_submenu("select", select_vertex)
v.add_submenu("select", select_edge)
v.add_submenu("select", select_face)
# Add menu for screencapture
v.add_menu("screenshot")
v.add_submenu("screenshot", dump)

# Display a solid
compound = Compound.load_from_step(pathlib.Path(__file__).resolve().parent.joinpath("example.stp"))
solid = next(compound.solids())
v.display(solid, transparency=0.5)
# Set the selection mode to face
v.selection_mode_face()

# Tooltip that's displayed an entity is clicked on
tooltip = None


def callback(selected_shapes, x, y):
    global tooltip
    # If nothing is selected then return
    if len(selected_shapes) == 0:
        return
    # Keep only one tooltip active
    if tooltip is not None:
        tooltip.Erase()
    # Assume that only one entity is selected
    entity = selected_shapes[0]
    if type(entity) == Face:
        uv = entity.uv_bounds().center()
        pt = entity.point(uv)
        tooltip = v.display_text(pt, entity.surface_type(), height=30)
    elif type(entity) == Edge:
        u = entity.u_bounds().middle()
        pt = entity.point(u)
        tooltip = v.display_text(pt, entity.curve_type(), height=30)
    elif type(entity) == Vertex:
        pt = entity.point()
        tooltip = v.display_text(
            pt, f"{pt[0]:2.3f}, {pt[1]:2.3f}, {pt[2]:2.3f}", height=30
        )


# Register callback
v.on_select(callback)

# Show
v.fit()
v.show()
