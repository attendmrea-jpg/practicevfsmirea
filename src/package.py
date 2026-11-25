class Package:
    def __init__(self, name, version=""):
        self.name = name
        self.version = version

    @property
    def label(self):
        if not self.version:
            return self.name
        return self.name + " " + self.version

    def __eq__(self, other):
        return (self.name, self.version) == (other.name, other.version)

    def __lt__(self, other):
        return (self.name, self.version) < (other.name, other.version)

    def __hash__(self):
        return hash((self.name, self.version))

    def __repr__(self):
        return self.label
