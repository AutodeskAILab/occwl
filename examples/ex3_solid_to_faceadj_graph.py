import numpy as np
from occwl.solid import Solid
from occwl.viewer import Viewer
from occwl.graph import face_adjacency


example = Solid.make_box(10, 10, 10)
# example = Solid.make_sphere(10, (0, 0, 0))
g = face_adjacency(example, self_loops=True)

print(f"Number of nodes (faces): {len(g.nodes)}")
print(f"Number of edges: {len(g.edges)}")

v = Viewer(backend="wx")
v.display(example, transparency=0.8)

# Get the points at each face's center
face_centers = {}
for face_idx in g.nodes():
    # Display a sphere for each face's center
    face = g.nodes[face_idx]["face"]
    parbox = face.uv_bounds()
    umin, vmin = parbox.min_point()
    umax, vmax = parbox.max_point()
    center_uv = (umin + 0.5 * (umax - umin), vmin + 0.5 * (vmax - vmin))
    center = face.point(center_uv)
    v.display(Solid.make_sphere(center=center, radius=0.25))
    face_centers[face_idx] = center

for fi, fj in g.edges():
    pt1 = face_centers[fi]
    pt2 = face_centers[fj]
    # Make a cylinder for each edge connecting a pair of faces
    up_dir = pt2 - pt1
    height = np.linalg.norm(up_dir)
    if height > 1e-3:
        v.display(
            Solid.make_cylinder(
                radius=0.2, height=height, base_point=pt1, up_dir=up_dir
            )
        )

# Show the viewer
v.fit()
v.show()
