import unittest

from src.graph import build, find_cycles
from src.package import Package
from src.report import format_cycles, format_graph
from src.sources import TestSource

DEEP = {
    "A": ["B", "C"],
    "B": ["D", "E"],
    "C": ["E", "F"],
    "D": ["G"],
    "E": ["G"],
    "F": ["G"],
    "G": [],
}
CYCLE = {"A": ["B"], "B": ["C"], "C": ["A"]}
INNER = {"A": ["B"], "B": ["C", "E"], "C": ["D"], "D": ["B"], "E": []}
SELF = {"A": ["A"]}


def graph_of(table, root="A"):
    return build(TestSource(table), Package(root))


class BuildTest(unittest.TestCase):
    def test_all_nodes_are_found(self):
        self.assertEqual(len(graph_of(DEEP).nodes), len(DEEP))

    def test_nodes_are_found_level_by_level(self):
        labels = [node.label for node in graph_of(DEEP).nodes]
        self.assertEqual(labels, ["A", "B", "C", "D", "E", "F", "G"])

    def test_shared_dependency_is_single_node(self):
        graph = graph_of(DEEP)
        self.assertEqual(
            [node.label for node in graph.nodes].count("G"), 1
        )

    def test_shared_dependency_keeps_both_edges(self):
        graph = graph_of(DEEP)
        parents = [
            parent.label for parent, child in graph.pairs()
            if child.label == "E"
        ]
        self.assertEqual(sorted(parents), ["B", "C"])

    def test_package_without_dependencies(self):
        graph = graph_of({"A": []})
        self.assertEqual(graph.pairs(), [])

    def test_transitive_edges_are_kept(self):
        graph = graph_of(DEEP)
        pairs = [
            (parent.label, child.label) for parent, child in graph.pairs()
        ]
        self.assertIn(("D", "G"), pairs)


class CycleTest(unittest.TestCase):
    def test_graph_with_cycle_is_finite(self):
        self.assertEqual(len(graph_of(CYCLE).nodes), len(CYCLE))

    def test_cycle_is_reported(self):
        cycles = find_cycles(graph_of(CYCLE))
        self.assertEqual(len(cycles), 1)

    def test_cycle_starts_and_ends_at_same_node(self):
        cycle = find_cycles(graph_of(CYCLE))[0]
        self.assertEqual(cycle[0], cycle[-1])

    def test_inner_cycle_is_reported(self):
        cycle = find_cycles(graph_of(INNER))[0]
        labels = [node.label for node in cycle]
        self.assertEqual(labels, ["B", "C", "D", "B"])

    def test_self_dependency(self):
        self.assertEqual(len(find_cycles(graph_of(SELF))), 1)

    def test_graph_without_cycles(self):
        self.assertEqual(find_cycles(graph_of(DEEP)), [])


class ReportTest(unittest.TestCase):
    def test_graph_title_counts_nodes_and_edges(self):
        text = format_graph(graph_of(DEEP))
        self.assertIn("узлов: 7", text)
        self.assertIn("рёбер: 9", text)

    def test_edges_are_printed(self):
        self.assertIn("A -> B", format_graph(graph_of(DEEP)))

    def test_empty_graph(self):
        self.assertIn("зависимостей нет", format_graph(graph_of({"A": []})))

    def test_cycles_are_printed(self):
        text = format_cycles(find_cycles(graph_of(CYCLE)))
        self.assertIn("A -> B -> C -> A", text)


if __name__ == "__main__":
    unittest.main()
