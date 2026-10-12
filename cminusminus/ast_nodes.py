from dataclasses import dataclass


@dataclass(frozen=True)
class Number:
    value: int | float


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


Node = Number | UnaryOperation | BinaryOperation