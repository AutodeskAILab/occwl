import os
import sys
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from occwl.solid import Solid
from occwl.viewer import Viewer
from occwl.graph import face_adjacency, vertex_adjacency
import math

box = Solid.make_box(10, 10, 10)
g = vertex_adjacency(box, self_loops=True)

v = Viewer(backend="wx")
# Get the points for each vertex
points = {}
for i, vert in enumerate(g.nodes):
    pt = vert.point()
    points[g.nodes[vert]["index"]] = pt
    v.display(Solid.make_sphere(center=pt, radius=0.25))

# Make a cylinder for each edge connecting a pair of vertices
for vi, vj in g.edges:
    pt1 = np.asarray(points[g.nodes[vi]["index"]])
    pt2 = np.asarray(points[g.nodes[vj]["index"]])
    up_dir = pt2 - pt1
    v.display(Solid.make_cylinder(radius=0.2, height=np.linalg.norm(up_dir), base_point=pt1, up_dir=up_dir))

# Show the viewer
v.fit()
v.show()
