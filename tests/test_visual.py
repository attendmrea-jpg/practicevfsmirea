import unittest
import xml.dom.minidom

from src import mermaid, svg
from src.graph import build
from src.package import Package
from src.sources import TestSource

DEEP = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["D"],
    "D": [],
}
SINGLE = {"A": []}
CYCLE = {"A": ["B"], "B": ["A"]}


def graph_of(table):
    return build(TestSource(table), Package("A"))


def real_graph():
    table = {"serde_json 1.0.133": []}
    return build(TestSource(table), Package("serde_json", "1.0.133"))


class MermaidTest(unittest.TestCase):
    def setUp(self):
        self.text = mermaid.render(graph_of(DEEP))

    def test_diagram_header(self):
        self.assertTrue(self.text.startswith("graph TD"))

    def test_every_node_is_declared(self):
        for label in ("A", "B", "C", "D"):
            self.assertIn('["' + label + '"]', self.text)

    def test_edges_are_declared(self):
        self.assertEqual(self.text.count(" --> "), 4)

    def test_identifiers_are_unique(self):
        names = mermaid.node_names(graph_of(DEEP))
        self.assertEqual(len(set(names.values())), len(names))

    def test_version_is_part_of_the_label(self):
        text = mermaid.render(real_graph())
        self.assertIn('["serde_json 1.0.133"]', text)

    def test_cycle_is_drawn(self):
        text = mermaid.render(graph_of(CYCLE))
        self.assertEqual(text.count(" --> "), 2)


class SvgTest(unittest.TestCase):
    def setUp(self):
        self.text = svg.render(graph_of(DEEP))
        self.document = xml.dom.minidom.parseString(self.text)

    def test_document_is_valid_xml(self):
        self.assertEqual(self.document.documentElement.tagName, "svg")

    def test_canvas_has_size(self):
        root = self.document.documentElement
        self.assertGreater(int(root.getAttribute("width")), 0)
        self.assertGreater(int(root.getAttribute("height")), 0)

    def test_every_node_is_drawn(self):
        boxes = self.document.getElementsByTagName("rect")
        self.assertEqual(len(boxes), len(DEEP))

    def test_every_edge_is_drawn(self):
        lines = self.document.getElementsByTagName("line")
        self.assertEqual(len(lines), 4)

    def test_labels_are_printed(self):
        texts = self.document.getElementsByTagName("text")
        drawn = {item.firstChild.nodeValue for item in texts}
        self.assertEqual(drawn, set(DEEP))

    def test_root_is_highlighted(self):
        boxes = self.document.getElementsByTagName("rect")
        self.assertNotEqual(
            boxes[0].getAttribute("fill"), boxes[1].getAttribute("fill")
        )

    def test_single_package(self):
        document = xml.dom.minidom.parseString(svg.render(graph_of(SINGLE)))
        self.assertEqual(len(document.getElementsByTagName("rect")), 1)

    def test_deeper_nodes_are_lower(self):
        boxes = self.document.getElementsByTagName("rect")
        self.assertLess(
            float(boxes[0].getAttribute("y")),
            float(boxes[1].getAttribute("y")),
        )


if __name__ == "__main__":
    unittest.main()
