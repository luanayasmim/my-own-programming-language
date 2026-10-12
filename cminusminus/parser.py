import math

from .ast_nodes import BinaryOperation, Node, Number, UnaryOperation
from .errors import ParserError
from .lexer import Token, tokenize


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.index]

    def advance(self) -> Token:
        token = self.current
        self.index += 1
        return token

    def parse(self) -> Node:
        node = self.expression()
        if self.current.kind != "EOF":
            raise ParserError(f"Token inesperado: {self.current.text!r}", self.current.position)
        return node

    def expression(self) -> Node:
        node = self.term()
        while self.current.kind in ("+", "-"):
            operator = self.advance()
            node = BinaryOperation(node, operator.kind, self.term(), operator.position)
        return node

    def term(self) -> Node:
        node = self.unary()
        while self.current.kind in ("*", "/"):
            operator = self.advance()
            node = BinaryOperation(node, operator.kind, self.unary(), operator.position)
        return node

    def unary(self) -> Node:
        if self.current.kind in ("+", "-"):
            operator = self.advance()
            return UnaryOperation(operator.kind, self.unary(), operator.position)
        return self.primary()

    def primary(self) -> Node:
        token = self.current
        if token.kind == "NUMBER":
            self.advance()
            try:
                value = float(token.text) if "." in token.text else int(token.text)
            except ValueError as error:
                raise ParserError("Numero excede o limite suportado", token.position) from error
            if isinstance(value, float) and not math.isfinite(value):
                raise ParserError("Numero excede o limite suportado", token.position)
            return Number(value)
        if token.kind == "(":
            self.advance()
            node = self.expression()
            if self.current.kind != ")":
                raise ParserError("Esperado ')'", self.current.position)
            self.advance()
            return node
        raise ParserError("Esperado um numero ou '('", token.position)


def parse(source: str) -> Node:
    return Parser(tokenize(source)).parse()