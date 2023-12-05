

class ParseError(Exception):
    """Raised for errors encountered during Parsing."""


class Parser:
    def __init__(self, scanner):
        self.scanner = scanner

    def parse(self):
        pass
