INDENT = "  "
ARROW = " -> "
EMPTY_GRAPH = "зависимостей нет"
CYCLES_TITLE = "циклические зависимости:"


def format_graph(graph):
    lines = [_graph_title(graph)]
    pairs = graph.pairs()
    if not pairs:
        lines.append(INDENT + EMPTY_GRAPH)
    for parent, child in pairs:
        lines.append(INDENT + parent.label + ARROW + child.label)
    return "\n".join(lines)


def format_cycles(cycles):
    lines = [CYCLES_TITLE]
    for cycle in cycles:
        lines.append(INDENT + ARROW.join(item.label for item in cycle))
    return "\n".join(lines)


def _graph_title(graph):
    return (
        "граф зависимостей " + graph.root.label
        + " (узлов: " + str(len(graph.nodes))
        + ", рёбер: " + str(len(graph.pairs())) + "):"
    )
