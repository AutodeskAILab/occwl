"""
Test that the size of native occ files is reduced when they are saved without
the triangles
"""

# System
from pathlib import Path
import tempfile
import numpy as np

# OCC
from occwl.compound import Compound
from OCC.Core import PYTHONOCC_VERSION_MAJOR, PYTHONOCC_VERSION_MINOR

# Test
from tests.test_base import TestBase

class ReduceNativeFileSizeTester(TestBase):
    def test_reduce_native_file_size(self):
        data_folder = self.test_folder() / "test_data"
        native_file = data_folder / "brep_files_big/00001664_2a82acbc007f4faebe261cb8_step_000_0000.brep"
        self.check_file_size_reduced(native_file)

    def check_file_size_reduced(self, native_file):
        temp_dir = tempfile.TemporaryDirectory()
        size_before = native_file.stat().st_size
        shp = Compound.load_from_occ_native(native_file)
        output_file = Path(temp_dir.name) / (native_file.stem + ".brep")
        shp.save_to_occ_native(output_file)
        size_after = output_file.stat().st_size
        percent_saving = (size_before-size_after)/size_before
        print(f"File {native_file.stem}  Before {size_before}  After {size_after}   Saving {percent_saving}%")
        self.assertLess(size_after, 0.74*size_before, msg="Test the files is much smaller")

        comp = Compound.load_from_occ_native(output_file)
        self.assertTrue(isinstance(comp, Compound), msg="Should load a compound")