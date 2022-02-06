import numpy as np
from occwl.solid import Solid
from occwl.viewer import Viewer
from occwl.graph import vertex_adjacency

example = Solid.make_box(10, 10, 10)
# example = Solid.make_sphere(10, (0, 0, 0))
g = vertex_adjacency(example, self_loops=True)

print(f"Number of nodes (vertices): {len(g.nodes)}")
print(f"Number of edges: {len(g.edges)}")

v = Viewer(backend="wx")
v.display(example, transparency=0.5)
# Get the points for each vertex
points = {}
for vert_idx in g.nodes:
    pt = g.nodes[vert_idx]["vertex"].point()
    points[vert_idx] = pt
    v.display(Solid.make_sphere(center=pt, radius=0.25))

# Make a cylinder for each edge connecting a pair of vertices
for vi, vj in g.edges:
    pt1 = points[vi]
    pt2 = points[vj]
    up_dir = pt2 - pt1
    if np.linalg.norm(up_dir) < 1e-6:
        # This must be a loop with one Vertex
        continue
    v.display(
        Solid.make_cylinder(
            radius=0.2, height=np.linalg.norm(up_dir), base_point=pt1, up_dir=up_dir
        )
    )

# Show the viewer
v.fit()
v.show()
