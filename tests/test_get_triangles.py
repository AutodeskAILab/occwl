
# System
import numpy as np
from pathlib import Path

from occwl.geometry.tri_utils import write_obj 

# Test
from test_base import TestBase

class TriangleTester(TestBase):
        
    def test_triangles(self):
        data_folder = self.test_folder() / "test_data"
        self.run_test_on_all_files_in_folder(data_folder)

    def check_tris(self, verts, tris):
        for v in verts:
            self.assertTrue(v.size == 3)
            
        for tri in tris:
            self.assertTrue(isinstance(tri, list))
            self.assertTrue(len(tri)==3)
            for index in tri:
                self.assertTrue(isinstance(index, int))
                self.assertTrue(index < len(verts))

    def run_test_with_pathname(self, file, solid):
        verts, tris = solid.get_triangles()
        self.assertTrue(verts is not None)
        self.assertTrue(tris is not None)
        self.check_tris(verts, tris)

        output_folder = Path("results")
        if not output_folder.exists():
            output_folder.mkdir()
        output_pathname = (output_folder / file.stem).with_suffix(".obj")
        write_obj(output_pathname, verts, tris)
