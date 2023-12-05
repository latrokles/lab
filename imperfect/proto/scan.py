

class ScanError(Exception):
    """Raised for errors encountered during Scanning."""


class Scanner:
    def __init__(self, src):
        self.src = src
        self.pos = 0
        self.col = 0
        self.row = 0

    def scan(self):
        return self.src.split()

    def emit_error(self, message):
        pass

    def scan_token(self):
        pass

    def skip_token(self):
        pass
