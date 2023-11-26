import enum

from dataclasses import dataclass


@enum.unique
class TokenKind(enum.Enum):
    PAREN_OPEN = enum.auto()
    PAREN_CLOSE = enum.auto()
    BRACKET_OPEN = enum.auto()
    BRACKET_CLOSE = enum.auto()
    BRACE_OPEN = enum.auto()
    BRACE_CLOSE = enum.auto()
    PIPE = enum.auto()
    COMMA = enum.auto()
    DOT = enum.auto()
    EQUAL = enum.auto()
    COLON = enum.auto()
    SEMICOLON = enum.auto()
    EOF = enum.auto()


@dataclass
class Token:
    kind: TokenKind
    lexeme: str
    value: ...
    row: int
    col: int
