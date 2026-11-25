HEADER = "graph TD"
INDENT = "    "
NODE_PREFIX = "n"
EDGE = " --> "
QUOTE = '"'
REPLACEMENTS = (('"', "'"), ("[", "("), ("]", ")"))


def render(graph):
    names = node_names(graph)
    lines = [HEADER]
    for node in graph.nodes:
        lines.append(INDENT + names[node] + _box(node))
    for parent, child in graph.pairs():
        lines.append(INDENT + names[parent] + EDGE + names[child])
    return "\n".join(lines)


def node_names(graph):
    names = {}
    for number, node in enumerate(graph.nodes):
        names[node] = NODE_PREFIX + str(number)
    return names


def _box(node):
    return "[" + QUOTE + _escape(node.label) + QUOTE + "]"


def _escape(text):
    for source, target in REPLACEMENTS:
        text = text.replace(source, target)
    return text
