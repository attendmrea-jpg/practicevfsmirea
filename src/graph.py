ACTIVE = 1
DONE = 2


class Graph:
    def __init__(self, root):
        self.root = root
        self.nodes = [root]
        self.edges = {root: []}

    def add(self, node):
        self.nodes.append(node)
        self.edges[node] = []

    def connect(self, parent, child):
        if child not in self.edges[parent]:
            self.edges[parent].append(child)

    def children(self, node):
        return self.edges.get(node, [])

    def has(self, node):
        return node in self.edges

    def pairs(self):
        found = []
        for node in self.nodes:
            for child in self.children(node):
                found.append((node, child))
        return found


def build(source, root):
    graph = Graph(root)
    _visit(source, graph, [root])
    return graph


def _visit(source, graph, level):
    if not level:
        return
    following = []
    for node in level:
        following.extend(_expand(source, graph, node))
    _visit(source, graph, following)


def _expand(source, graph, node):
    discovered = []
    for child in source.direct(node):
        if not graph.has(child):
            graph.add(child)
            discovered.append(child)
        graph.connect(node, child)
    return discovered


def find_cycles(graph):
    state = {}
    found = []
    for node in graph.nodes:
        _search(graph, node, state, [], found)
    return _unique(found)


def _search(graph, node, state, path, found):
    if state.get(node) == DONE:
        return
    if state.get(node) == ACTIVE:
        found.append(_cycle_from(path, node))
        return
    state[node] = ACTIVE
    path.append(node)
    for child in graph.children(node):
        _search(graph, child, state, path, found)
    path.pop()
    state[node] = DONE


def _cycle_from(path, node):
    return path[path.index(node):] + [node]


def _unique(cycles):
    seen = set()
    found = []
    for cycle in cycles:
        key = frozenset(item.label for item in cycle)
        if key not in seen:
            seen.add(key)
            found.append(cycle)
    return found


def load_order(graph):
    pending = {node: set(graph.children(node)) for node in graph.nodes}
    order = []
    ready = _ready(pending)
    while ready:
        order.extend(ready)
        _remove(pending, ready)
        ready = _ready(pending)
    return order, sorted(pending)


def _ready(pending):
    return sorted(node for node, waited in pending.items() if not waited)


def _remove(pending, ready):
    for node in ready:
        del pending[node]
    for waited in pending.values():
        waited.difference_update(ready)
