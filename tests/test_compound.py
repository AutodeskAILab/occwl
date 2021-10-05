from occwl.compound import Compound

# Test
from tests.test_base import TestBase


class CompoundTester(TestBase):
    def test_compound(self):
        data_folder = self.test_folder() / "test_data"
        compound_file = data_folder / "ManyBodies.stp"

        compound = load_single_compound_from_step(compound_file)
        num_solids = 0
        solids = list(compound.solids())
        self.assertEqual(len(solids), 2)
        