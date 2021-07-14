import pathlib
import numpy as np
from occwl.graph import face_adjacency
from occwl.io import load_step
from occwl.solid import Solid
from occwl.uvgrid import uvgrid
from occwl.viewer import Viewer

# example = Solid.make_box(10, 10, 10)
# example = Solid.make_sphere(10, (0, 0, 0))
example = Solid.make_cylinder(5, 10)
# example = load_step(pathlib.Path(__file__).resolve().parent.joinpath("example.stp"))[0]
g = face_adjacency(example, self_loops=True)

bbox = example.box()
point_radius = min(bbox.x_length(), bbox.y_length(), bbox.z_length()) * 0.03
arrow_radius = point_radius * 0.85
arrow_length = arrow_radius * 4
edge_radius = point_radius * 0.9

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
v.display(example, transparency=0.3)

# Get the points at each face's center for visualizing edges
face_centers = {}
for face_idx in g.nodes():
    # Display a sphere for each UV-grid point
    face = g.nodes[face_idx]["face"]
    grid = face_grids[face_idx]
    for row in range(grid["points"].shape[0]):
        for col in range(grid["points"].shape[1]):
            if grid["mask"][row, col] == 1:
                sphere = Solid.make_sphere(
                    center=grid["points"][row, col], radius=point_radius
                )
                v.display(sphere, color="BLACK")
                arrow = Solid.make_cone(
                    arrow_radius,
                    0,
                    height=arrow_length,
                    up_dir=grid["normals"][row, col],
                )
                arrow.translate(grid["points"][row, col])
                v.display(
                    arrow, color="RED",
                )
    face_centers[face_idx] = grid["points"][4, 4]

for fi, fj in g.edges():
    pt1 = face_centers[fi]
    pt2 = face_centers[fj]
    # Make a cylinder for each edge connecting a pair of faces
    up_dir = pt2 - pt1
    height = np.linalg.norm(up_dir)
    if height > 1e-3:
        v.display(
            Solid.make_cylinder(
                radius=edge_radius, height=height, base_point=pt1, up_dir=up_dir
            ),
            color="GREEN",
        )

# Show the viewer
v.fit()
v.show()
