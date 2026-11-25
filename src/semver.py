import re

from src.errors import RegistryError

VERSION_PATTERN = re.compile(
    r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:[-+]([0-9A-Za-z.\-+]*))?$"
)
OPERATORS = (">=", "<=", "=", ">", "<", "^", "~")
CARET = "^"
TILDE = "~"
ANY = ("*", "x", "X", "")
ZERO = 0
MAJOR_INDEX = 0
MINOR_INDEX = 1
PATCH_INDEX = 2


class Version:
    def __init__(self, parts, prerelease="", text=""):
        self.parts = parts
        self.prerelease = prerelease
        self.text = text or ".".join(str(part) for part in parts)

    @property
    def is_prerelease(self):
        return bool(self.prerelease)

    def __eq__(self, other):
        return self.parts == other.parts

    def __lt__(self, other):
        return self.parts < other.parts

    def __hash__(self):
        return hash(self.parts)


def parse_version(text):
    match = VERSION_PATTERN.match(text.strip())
    if match is None:
        raise RegistryError("неразбираемая версия: " + text)
    groups = match.groups()[:PATCH_INDEX + 1]
    numbers = tuple(int(group) if group else ZERO for group in groups)
    return Version(numbers, match.group(4) or "", text.strip())


def matches(version, requirement):
    for operator, bound in conditions(requirement):
        if not _compare(version, operator, bound):
            return False
    return True


def select(versions, requirement):
    allowed = [
        version for version in versions
        if not version.is_prerelease and matches(version, requirement)
    ]
    if not allowed:
        return None
    return max(allowed)


def conditions(requirement):
    found = []
    for part in requirement.split(","):
        found.extend(_single(part.strip()))
    return found


def _single(text):
    if text in ANY:
        return []
    operator, rest = _split(text)
    if "*" in rest or "x" in rest or "X" in rest:
        return _wildcard(rest)
    if operator in (CARET, ""):
        return _caret(rest)
    if operator == TILDE:
        return _tilde(rest)
    return [(operator, parse_version(rest))]


def _split(text):
    for operator in OPERATORS:
        if text.startswith(operator):
            return operator, text[len(operator):].strip()
    return "", text


def _caret(text):
    low = parse_version(text)
    index = _first_nonzero(low.parts, _given(text))
    return [(">=", low), ("<", _bump(low.parts, index))]


def _tilde(text):
    low = parse_version(text)
    index = MINOR_INDEX if _given(text) > 1 else MAJOR_INDEX
    return [(">=", low), ("<", _bump(low.parts, index))]


def _wildcard(text):
    kept = []
    for part in text.split("."):
        if part in ANY:
            break
        kept.append(part)
    if not kept:
        return []
    low = parse_version(".".join(kept))
    return [(">=", low), ("<", _bump(low.parts, len(kept) - 1))]


def _given(text):
    head = text.split("-")[0].split("+")[0]
    return min(len(head.split(".")), PATCH_INDEX + 1)


def _first_nonzero(parts, given):
    for index in range(given):
        if parts[index] != ZERO:
            return index
    return given - 1


def _bump(parts, index):
    raised = list(parts[:index]) + [parts[index] + 1]
    while len(raised) < len(parts):
        raised.append(ZERO)
    return Version(tuple(raised))


COMPARISONS = {
    ">=": lambda left, right: left.parts >= right.parts,
    "<=": lambda left, right: left.parts <= right.parts,
    ">": lambda left, right: left.parts > right.parts,
    "<": lambda left, right: left.parts < right.parts,
    "=": lambda left, right: left.parts == right.parts,
}


def _compare(version, operator, bound):
    return COMPARISONS[operator](version, bound)
