
# System
import numpy as np

# Test
from test_base import TestBase

class FaceTester(TestBase):
        
    def test_face(self):
        data_folder = self.test_folder() / "test_data"
        self.run_test_on_all_files_in_folder(data_folder)

    def perform_tests_on_face(self, face):
        


    def run_test(self, solid):
        faces = solid.faces()
        for face in faces:
            self.perform_tests_on_face(face)
