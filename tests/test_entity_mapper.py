
# PythonOCC
from OCC.Extend.TopologyUtils import TopologyExplorer, WireExplorer

# occwl
from occwl.entity_mapper import EntityMapper

# Tests
from tests.test_base import TestBase

class EntityMapperTester(TestBase):

    def test_entity_mapper(self):
        data_folder = self.test_folder() / "test_data"
        self.run_test_on_all_files_in_folder(data_folder)

    def check_face_order(self, entity_mapper, solid):
        top_exp = TopologyExplorer(solid)
        faces = top_exp.faces()
        for index, face in enumerate(faces):
            f = Face(face)
            mapped_index = entity_mapper.face_index(w)
            self.assertEqual(mapped_index, index)

    def check_wire_order(self, entity_mapper, solid):
        top_exp = TopologyExplorer(solid)
        wires = top_exp.wires()
        for index, wire in enumerate(wires):
            w = Wire(wire)
            mapped_index = entity_mapper.wire_index(w)
            self.assertEqual(mapped_index, index)

    def check_edge_order(self, entity_mapper, solid):
        top_exp = TopologyExplorer(solid)
        edges = top_exp.edges()
        for edge in edges:
            e = Edge(edge)
            mapped_index = entity_mapper.edge_index(e)
            self.assertEqual(mapped_index, index)
           

    def check_oriented_edge_order(self, entity_mapper, solid):
        oriented_top_exp = TopologyExplorer(body, ignore_orientation=False)
        index = 0
        for wire in oriented_top_exp.wires():
            wire_exp = WireExplorer(wire)
            for oriented_edge in wire_exp.ordered_edges():
                oe = Edge(oriented_edge)
                mapped_index = entity_mapper.oriented_edge_index(v)
                self.assertEqual(mapped_index, index)
                index += 1

    def check_vertex_order(self, entity_mapper, solid):
        top_exp = TopologyExplorer(solid)
        vertices = top_exp.vertices()
        for index, vertex in enumerate(vertices):
            v = Vertex(vertex)
            mapped_index = entity_mapper.vertex_index(v)
            self.assertEqual(mapped_index, index)


    def run_test(self, solid):
        """
        Test the entity mapper works for this solid
        """
        entity_mapper = EntityMapper(solid)
        self.check_face_order(entity_mapper, solid)
        self.check_wire_order(entity_mapper, solid)
        self.check_edge_order(entity_mapper, solid)
        self.check_oriented_edge_order(entity_mapper, solid)
        self.check_vertex_order(entity_mapper, solid)