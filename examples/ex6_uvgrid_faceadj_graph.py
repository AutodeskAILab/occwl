import pathlib
import numpy as np
from occwl.graph import face_adjacency
from occwl.solid import Solid
from occwl.edge import Edge
from occwl.uvgrid import uvgrid
from occwl.viewer import Viewer

# example = Solid.make_box(10, 10, 10)
# example = Solid.make_sphere(10, (0, 0, 0))
example = Solid.make_cylinder(5, 10)
# compound = Compound.load_from_step(pathlib.Path(__file__).resolve().parent.joinpath("example.stp"))
# example = next(compound.solids())
g = face_adjacency(example, self_loops=True)
assert g is not None

bbox = example.box()
point_radius = bbox.max_box_length() * 0.03
arrow_radius = point_radius * 0.85
arrow_length = arrow_radius * 4

face_grids = {}
for face_idx in g.nodes:
    face = g.nodes[face_idx]["face"]
    points = uvgrid(face, num_u=10, num_v=10, method="point")
    mask = uvgrid(face, num_u=10, num_v=10, method="inside")
    normals = uvgrid(face, num_u=10, num_v=10, method="normal")
    face_grids[face_idx] = {"points": points, "normals": normals, "mask": mask}

print(f"Number of nodes (faces): {len(g.nodes)}")
print(f"Number of edges: {len(g.edges)}")

v = Viewer(backend="wx")
v.display(example, transparency=0.6, color=(0.2, 0.2, 0.2))

# Get the points at each face's center for visualizing edges
face_centers = {}
for face_idx in g.nodes():
    # Display a sphere for each UV-grid point
    face = g.nodes[face_idx]["face"]
    grid = face_grids[face_idx]
    # Display points
    face_points = grid["points"].reshape((-1, 3))
    face_mask = grid["mask"].reshape(-1)
    face_points = face_points[face_mask, :]
    v.display_points(face_points, marker="point", color="GREEN")
    # Display normals
    face_normals = grid["normals"].reshape((-1, 3))
    face_normals = face_normals[face_mask, :]
    lines = [Edge.make_line_from_points(pt, pt + arrow_length * nor) for pt, nor in zip(face_points, face_normals)]
    for l in lines:
        v.display(l, color="RED")
    face_centers[face_idx] = grid["points"][4, 4]

for fi, fj in g.edges():
    pt1 = face_centers[fi]
    pt2 = face_centers[fj]
    dist = np.linalg.norm(pt2 - pt1)
    if dist > 1e-3:
        v.display(Edge.make_line_from_points(pt1, pt2), color=(51.0 / 255.0, 0, 1))

# Show the viewer
v.fit()
v.show()
