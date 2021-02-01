import os
import sys
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from occam.solid import Solid
from occam.viewer import Viewer
from occam.graph import face_adjacency, vertex_adjacency
import math

box = Solid.make_box(10, 10, 10)
nodes, edges, connectivity = vertex_adjacency(box)

# Get the points for each vertex
points = []
for i, vert in enumerate(nodes):
    pt = vert.point()
    points.append(pt)

# Make a sphere for each vertex
v = Viewer()
for i, vert in enumerate(nodes):    
    v.display(Solid.make_sphere(center=points[i], radius=0.25))

# Make a cylinder for each edge connecting a pair of vertices
for conn in connectivity:
    pt1 = np.asarray(points[conn[0]])
    pt2 = np.asarray(points[conn[1]])
    up_dir = pt2 - pt1
    v.display(Solid.make_cylinder(radius=0.2, height=np.linalg.norm(up_dir), base_point=pt1, up_dir=up_dir))

# Show the viewer
v.fit()
v.show()
