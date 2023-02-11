# System
from pathlib import Path

# OCC
from occwl.compound import Compound

# Test
from tests.test_base import TestBase


class LoadWithNameTester(TestBase):

    def test_example(self):
        data_path = self.test_folder() / "test_data/import_tests"
        examples = [
            (
                "import_example_1.step", 
                ["DualZ v1 - BREP SOLID996",
                "DualZ v1 - BREP SOLID1000",
                "DualZ v1 - BREP SOLID1008",
                "DualZ v1 - BREP SOLID1012",
                "DualZ v1 - BREP SOLID1016",
                "DualZ v1 - BREP SOLID1020",
                "DualZ v1 - BREP SOLID1024",
                "screw mount"]
            ),
            ("block_through_hole.step", ["Body1"])
        ]
        for example in examples:
            pathname = data_path / example[0]
            expected_solid_names = example[1]
            self.check_for_example(pathname, expected_solid_names)

        print("Completed LoadWithNameTester")

    def check_for_example(self, pathname, expected_solid_names):
        self.assertTrue(pathname.exists())
        comp, shape_att = Compound.load_step_with_attributes(pathname)
        for s in comp.solids():
            self.assertTrue(s in shape_att)
            name = shape_att[s]["name"]
            self.assertTrue(name in expected_solid_names)

