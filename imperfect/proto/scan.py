from .token import Token, TokenKind

from imperfect.util import if_else


class ScanError(Exception):
    """Raised for errors encountered during Scanning."""


class Scanner:
    def __init__(self, src):
        self.src = src
        self.pos = 0
        self.col = 0
        self.row = 0
        self.start = 0
        self.tokens = []

    @property
    def src_length(self):
        return len(self.src)

    def scan(self):
        while self.is_not_at_end():
            self.start = self.pos
            self.scan_token()
        self.add_token(TokenKind.EOF, '', None)
        return self.tokens

    def is_at_end(self):
        return self.pos >= self.src_length

    def is_not_at_end(self):
        return self.pos < self.src_length

    def add_token(self, kind, lexeme, value):
        self.tokens.append(Token(kind, lexeme, value, self.row, self.pos))

    def scan_token(self):
        char = self.advance()
        match char:
            case '(':
                self.add_token(TokenKind.PAREN_OPEN, '(', None)
                return
            case ')':
                self.add_token(TokenKind.PAREN_CLOSE, ')', None)
                return
            case '[':
                self.add_token(TokenKind.BRACKET_OPEN, '[', None)
                return
            case ']':
                self.add_token(TokenKind.BRACKET_CLOSE, ']', None)
                return
            case '|':
                self.add_token(TokenKind.PIPE, '|', None)
                return
            case ':':
                # handle :
                # handle ::
                # handle :=
                # handle :ident
                return
            case '<':
                # handle <
                # handle <<
            case '-':
                # handle





        pass

    def emit_error(self, message):
        pass

    def skip_token(self):
        pass
