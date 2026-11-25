from xml.sax.saxutils import escape

MARGIN = 24
BOX_HEIGHT = 34
LEVEL_GAP = 96
COLUMN_GAP = 26
CHAR_WIDTH = 8
TEXT_PADDING = 24
FONT_SIZE = 13
TEXT_SHIFT = 5
RADIUS = 6
ROOT_FILL = "#d6e4ff"
NODE_FILL = "#f4f4f4"
STROKE = "#333333"
FONT = "monospace"
FIRST_LEVEL = 0


def render(graph):
    boxes = _layout(_levels(graph))
    width, height = _canvas(boxes)
    parts = [_header(width, height), _marker()]
    parts.extend(_edges(graph, boxes))
    parts.extend(_nodes(graph, boxes))
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def _levels(graph):
    depth = {graph.root: FIRST_LEVEL}
    queue = [graph.root]
    while queue:
        node = queue.pop(0)
        for child in graph.children(node):
            if child not in depth:
                depth[child] = depth[node] + 1
                queue.append(child)
    return _grouped(graph, depth)


def _grouped(graph, depth):
    levels = []
    for node in graph.nodes:
        while len(levels) <= depth[node]:
            levels.append([])
        levels[depth[node]].append(node)
    return levels


def _layout(levels):
    rows = [_row(level) for level in levels]
    widest = max(_row_width(row) for row in rows)
    boxes = {}
    for number, row in enumerate(rows):
        offset = (widest - _row_width(row)) / 2 + MARGIN
        boxes.update(_place(row, number, offset))
    return boxes


def _row(level):
    return [(node, _box_width(node)) for node in level]


def _row_width(row):
    widths = sum(width for _, width in row)
    return widths + COLUMN_GAP * (len(row) - 1)


def _place(row, number, offset):
    placed = {}
    left = offset
    top = MARGIN + number * LEVEL_GAP
    for node, width in row:
        placed[node] = (left, top, width)
        left += width + COLUMN_GAP
    return placed


def _box_width(node):
    return len(node.label) * CHAR_WIDTH + TEXT_PADDING


def _canvas(boxes):
    right = max(left + width for left, _, width in boxes.values())
    bottom = max(top for _, top, _ in boxes.values())
    return right + MARGIN, bottom + BOX_HEIGHT + MARGIN


def _header(width, height):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{0:.0f}" '
        'height="{1:.0f}" viewBox="0 0 {0:.0f} {1:.0f}">'
    ).format(width, height)


def _marker():
    return (
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" '
        'refX="8" refY="3" orient="auto">'
        '<path d="M0,0 L8,3 L0,6 z" fill="' + STROKE + '"/>'
        "</marker></defs>"
    )


def _edges(graph, boxes):
    lines = []
    for parent, child in graph.pairs():
        lines.append(_edge(boxes[parent], boxes[child]))
    return lines


def _edge(parent, child):
    start_x = parent[0] + parent[2] / 2
    start_y = parent[1] + BOX_HEIGHT
    end_x = child[0] + child[2] / 2
    end_y = child[1]
    return (
        '<line x1="{0:.0f}" y1="{1:.0f}" x2="{2:.0f}" y2="{3:.0f}" '
        'stroke="{4}" marker-end="url(#arrow)"/>'
    ).format(start_x, start_y, end_x, end_y, STROKE)


def _nodes(graph, boxes):
    lines = []
    for node in graph.nodes:
        fill = ROOT_FILL if node == graph.root else NODE_FILL
        lines.append(_node(node, boxes[node], fill))
    return lines


def _node(node, box, fill):
    left, top, width = box
    middle = top + BOX_HEIGHT / 2 + TEXT_SHIFT
    return (
        '<g><rect x="{0:.0f}" y="{1:.0f}" width="{2:.0f}" '
        'height="{3}" rx="{4}" fill="{5}" stroke="{6}"/>'
        '<text x="{7:.0f}" y="{8:.0f}" font-family="{9}" '
        'font-size="{10}" text-anchor="middle">{11}</text></g>'
    ).format(
        left, top, width, BOX_HEIGHT, RADIUS, fill, STROKE,
        left + width / 2, middle, FONT, FONT_SIZE, escape(node.label),
    )
