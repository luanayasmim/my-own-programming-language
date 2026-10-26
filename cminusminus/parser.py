import math

from .ast_nodes import (
    AssignmentStatement,
    BinaryOperation,
    CreateStatement,
    ExpressionStatement,
    Node,
    Number,
    ShowStatement,
    Statement,
    UnaryOperation,
    Variable,
)
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

    def parse_statement(self) -> Statement:
        if self.current.kind == "CREATE":
            self.advance()
            name = self.expect_identifier()
            self.expect("=")
            statement = CreateStatement(name.text, self.expression(), name.position)
        elif self.current.kind == "SHOW":
            self.advance()
            self.expect("(")
            expression = self.expression()
            self.expect(")")
            statement = ShowStatement(expression)
        elif self.current.kind == "IDENTIFIER" and self.tokens[self.index + 1].kind == "=":
            name = self.advance()
            self.advance()
            statement = AssignmentStatement(name.text, self.expression(), name.position)
        else:
            statement = ExpressionStatement(self.expression())
        if self.current.kind != "EOF":
            raise ParserError(f"Token inesperado: {self.current.text!r}", self.current.position)
        return statement

    def expect(self, kind: str) -> Token:
        if self.current.kind != kind:
            expected = "um identificador" if kind == "IDENTIFIER" else repr(kind)
            raise ParserError(f"Esperado {expected}", self.current.position)
        return self.advance()

    def expect_identifier(self) -> Token:
        return self.expect("IDENTIFIER")

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
        if token.kind == "IDENTIFIER":
            self.advance()
            return Variable(token.text, token.position)
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


def parse_statement(source: str) -> Statement:
    return Parser(tokenize(source)).parse_statement()