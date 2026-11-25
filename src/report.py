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


ORDER_TITLE = "порядок загрузки зависимостей "
UNRESOLVED_TITLE = "не упорядочены из-за циклических зависимостей:"
NUMBER_SEPARATOR = ". "


def format_order(graph, order, unresolved):
    lines = [ORDER_TITLE + graph.root.label + ":"]
    for number, node in enumerate(order, start=1):
        lines.append(INDENT + str(number) + NUMBER_SEPARATOR + node.label)
    if unresolved:
        lines.append(UNRESOLVED_TITLE)
        for node in unresolved:
            lines.append(INDENT + node.label)
    return "\n".join(lines)
