# System
import unittest
import os
from pathlib import Path

import numpy as np

# OCC
from occwl.io import load_step

class TestBase(unittest.TestCase):

    def test_folder(self):
        return Path(os.path.dirname(__file__))

    def run_test_on_all_files_in_folder(self, folder):
        step_files = [ f for f in folder.glob("**/*.step")]
        stp_files = [ f for f in folder.glob("**/*.stp")]
        step_files.extend(stp_files)

        if len(step_files) == 0:
            self.fail("No files in directory")

        for file in step_files:
            print(f"Running tests for {file.stem}{file.suffix}")
            solids = load_step(file)
            for solid in solids: 
                self.run_test_with_pathname(file, solid)

    def run_test_with_pathname(self, file, solid):
        self.run_test(solid)

    def unitize_vector(self, vec):
        eps = 1e-7
        length = np.linalg.norm(vec)
        if length < eps:
            return None

        return vec / length


    def angle_between_vectors(self, v1, v2):
        """
        Return the angle between two vectors.
        If either vector has length close to zero then we will return 0.0
        """
        unit_v1 = self.unitize_vector(v1)
        unit_v2 = self.unitize_vector(v2)
        if unit_v1 is None or unit_v2 is None:
            # Case where one or both vectors had zero length
            return 0.0
        d = np.dot(unit_v1, unit_v2)
        d = np.clip(d, -1.0, 1.0)
        assert -1.0 <= d
        assert d <= 1.0
        return np.arccos(d)