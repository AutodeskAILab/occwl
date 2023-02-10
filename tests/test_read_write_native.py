# System
from pathlib import Path
import tempfile
import numpy as np

# OCC
from occwl.compound import Compound
from OCC.Core import PYTHONOCC_VERSION_MAJOR, PYTHONOCC_VERSION_MINOR

# Test
from tests.test_base import TestBase

class ReadWriteNativeTester(TestBase):
    def test_read_write_native(self):
        data_folder = self.test_folder() / "test_data"
        self.run_test_on_all_files_in_folder(data_folder)

        v2_test_data = data_folder / "brep_files_v2"
        self.load_brep_files(v2_test_data)

    def run_test(self, solid):
        self.run_test_on_version(solid, None)
        self.run_test_on_version(solid, 2)
        if PYTHONOCC_VERSION_MAJOR >= 7 and PYTHONOCC_VERSION_MINOR >= 6:
            self.run_test_on_version(solid, 3)

    def run_test_on_version(self, solid, version):
        temp_dir = tempfile.TemporaryDirectory()
        single_solid_file = Path(temp_dir.name) / "single_solid.brep"
        solid.save_to_occ_native(
            single_solid_file, 
            with_triangles=False,
            with_normals=False,
            format_version=version
        )
        comp = Compound.load_from_occ_native(single_solid_file)
        self.check_compound_same_as_solids(comp, [solid])

        multi_solid_file = Path(temp_dir.name) / "multi_solid.brep"

        
        # Translate 1 model unit in x
        mat = np.array([
            [1, 0, 0, 1],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        copy = solid.transform(mat, copy=True)
        solids = [ solid, copy]
        Compound.save_shapes_to_occ_native(
            multi_solid_file, 
            solids,
            with_triangles=False,
            with_normals=False,
            format_version=version
        )

        
        multi_solid_comp = Compound.load_from_occ_native(multi_solid_file)
        self.check_compound_same_as_solids(multi_solid_comp, solids)
        temp_dir.cleanup()



    def check_compound_same_as_solids(self, comp, solids):
        solids_from_comp = list(comp.solids())
        self.assertEqual(len(solids_from_comp), len(solids))
        for sfc, s in zip(solids_from_comp, solids):
            self.assertEqual(sfc.num_faces(), s.num_faces())
            self.assertEqual(sfc.num_edges(), s.num_edges())
            self.assertEqual(sfc.num_vertices(), s.num_vertices())

    def load_brep_files(self, v2_test_data):
        for file in v2_test_data.glob("*.brep"):
            comp = Compound.load_from_occ_native(file)
            solids_from_comp = list(comp.solids())
            self.assertGreater(len(solids_from_comp), 0)
