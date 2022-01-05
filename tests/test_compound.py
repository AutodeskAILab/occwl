from occwl.compound import Compound
from occwl.io import load_single_compound_from_step

# Test
from tests.test_base import TestBase


class CompoundTester(TestBase):
    def test_compound(self):
        data_folder = self.test_folder() / "test_data"
        compound_file = data_folder / "ManyBodies.stp"

        compound = Compound.load_from_step(compound_file)
        num_solids = compound.num_solids()
        solids = list(compound.solids())

        # We have 4 bodies.  Two are single shell solids
        # and two have internal voids
        #12=ADVANCED_BREP_SHAPE_REPRESENTATION('',(#435,#436,#13,#14),#704);
        #13=MANIFOLD_SOLID_BREP('',#433);
        #14=MANIFOLD_SOLID_BREP('',#434);
        #435=BREP_WITH_VOIDS('',#429,(#25));
        #436=BREP_WITH_VOIDS('',#431,(#26));
        self.assertEqual(len(solids), 4)
        self.assertEqual(num_solids, 4)
