from dataclasses import dataclass

Value = int | float | str


@dataclass(frozen=True)
class Number:
    value: int | float


@dataclass(frozen=True)
class StringLiteral:
    value: str


@dataclass(frozen=True)
class Variable:
    name: str
    position: int


@dataclass(frozen=True)
class UnaryOperation:
    operator: str
    operand: "Node"
    position: int


@dataclass(frozen=True)
class BinaryOperation:
    left: "Node"
    operator: str
    right: "Node"
    position: int


Node = Number | StringLiteral | Variable | UnaryOperation | BinaryOperation


@dataclass(frozen=True)
class ExpressionStatement:
    expression: Node


@dataclass(frozen=True)
class CreateStatement:
    name: str
    expression: Node
    position: int


@dataclass(frozen=True)
class AssignmentStatement:
    name: str
    expression: Node
    position: int


@dataclass(frozen=True)
class ShowStatement:
    expression: Node

@dataclass(frozen=True)
class IfStatement:
    condition: Node
    consequent: "Statement"
    position: int

Statement = ExpressionStatement | CreateStatement | AssignmentStatement | ShowStatement | IfStatement




