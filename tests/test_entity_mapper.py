
# PythonOCC
from OCC.Extend.TopologyUtils import TopologyExplorer, WireExplorer

# occwl
from occwl.entity_mapper import EntityMapper
from occwl.solid import Solid
from occwl.face import Face
from occwl.edge import Edge
from occwl.wire import Wire
from occwl.vertex import Vertex

# Tests
from tests.test_base import TestBase

class EntityMapperTester(TestBase):

    def test_entity_mapper(self):
        data_folder = self.test_folder() / "test_data"
        # 100027_258e3965_0.stp fails test check_unique_coedges()
        # Note.  Open edges in example 118539_1dff9cf9_6.stp  Fails test check_closed()
        # 119129_8f04623b_0.stp fails test check_unique_coedges()
        # self.run_test_on_solid_from_filename("118539_1dff9cf9_6.stp")
        self.run_test_on_all_files_in_folder(data_folder)

    def check_face_order(self, entity_mapper, solid):
        top_exp = TopologyExplorer(solid.topods_solid())
        faces = top_exp.faces()
        for index, face in enumerate(faces):
            f = Face(face)
            mapped_index = entity_mapper.face_index(f)
            self.assertEqual(mapped_index, index)

    def check_wire_order(self, entity_mapper, solid):
        top_exp = TopologyExplorer(solid.topods_solid(), ignore_orientation=False)
        wires = top_exp.wires()
        for index, wire in enumerate(wires):
            w = Wire(wire)
            mapped_index = entity_mapper.wire_index(w)
            self.assertEqual(mapped_index, index)

    def check_edge_order(self, entity_mapper, solid):
        top_exp = TopologyExplorer(solid.topods_solid())
        edges = top_exp.edges()
        for index, edge in enumerate(edges):
            e = Edge(edge)
            mapped_index = entity_mapper.edge_index(e)
            self.assertEqual(mapped_index, index)
           

    def check_oriented_edge_order(self, entity_mapper, solid):
        oriented_top_exp = TopologyExplorer(solid.topods_solid(), ignore_orientation=False)
        index = 0
        for wire in oriented_top_exp.wires():
            wire_exp = WireExplorer(wire)
            for oriented_edge in wire_exp.ordered_edges():
                oe = Edge(oriented_edge)
                mapped_index = entity_mapper.oriented_edge_index(oe)
                self.assertEqual(mapped_index, index)
                index += 1

    def check_vertex_order(self, entity_mapper, solid):
        top_exp = TopologyExplorer(solid.topods_solid())
        vertices = top_exp.vertices()
        for index, vertex in enumerate(vertices):
            v = Vertex(vertex)
            mapped_index = entity_mapper.vertex_index(v)
            self.assertEqual(mapped_index, index)

    def check_unique_oriented_edges(self, solid):
        oriented_edge_set = set()
        for wire in solid.wires():
            for oriented_edge in wire.ordered_edges():
                reversed = oriented_edge.reversed()
                tup = (oriented_edge, reversed)
                
                # We want to detect the case where the oriented edges
                # are not unique
                if tup in oriented_edge_set:
                    return False

                oriented_edge_set.add(tup)

        return True


    def run_test(self, solid):
        """
        Test the entity mapper works for this solid
        """
        if not self.check_unique_oriented_edges(solid):
            # The entity mapper doesn't support solids
            # with non-unique oriented edges
            return
        entity_mapper = EntityMapper(solid)
        self.check_face_order(entity_mapper, solid)
        self.check_wire_order(entity_mapper, solid)
        self.check_edge_order(entity_mapper, solid)
        self.check_oriented_edge_order(entity_mapper, solid)
        self.check_vertex_order(entity_mapper, solid)