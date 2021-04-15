import os
import sys
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from occwl.solid import Solid
from occwl.viewer import Viewer
from occwl.graph import face_adjacency
import math

box = Solid.make_box(10, 10, 10)
nodes, edges, connectivity = face_adjacency(box)

# Get the center points for each face's center
face_centers = []
for i, face in enumerate(nodes):
    umin, umax, vmin, vmax = face.uv_bounds()
    center_u, center_v = (0.5 * (umax - umin), vmin + 0.5 * (vmax - vmin))
    center = face.point(center_u, center_v)
    face_centers.append(center)

# Make a sphere for each face's center
v = Viewer()
for i, face in enumerate(nodes):    
    v.display(Solid.make_sphere(center=face_centers[i], radius=0.25))

# Make a cylinder for each edge connecting a pair of faces
for conn in connectivity:
    pt1 = np.asarray(face_centers[conn[0]])
    pt2 = np.asarray(face_centers[conn[1]])
    up_dir = pt2 - pt1
    v.display(Solid.make_cylinder(radius=0.2, height=np.linalg.norm(up_dir), base_point=pt1, up_dir=up_dir))

# Show the viewer
v.fit()
v.show()
