from collections.abc import MutableMapping
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
from .errors import EvaluationError


def evaluate(node: Node, variables: MutableMapping[str, int | float] | None = None) -> int | float:
    if isinstance(node, Number):
        return node.value
    if isinstance(node, Variable):
        if variables is None or node.name not in variables:
            raise EvaluationError(f"Variavel '{node.name}' nao foi criada", node.position)
        return variables[node.name]
    if isinstance(node, UnaryOperation):
        value = evaluate(node.operand, variables)
        if node.operator == "+":
            return value
        if node.operator == "-":
            return -value
        raise EvaluationError("Operador unario desconhecido", node.position)
    if isinstance(node, BinaryOperation):
        left = evaluate(node.left, variables)
        right = evaluate(node.right, variables)
        try:
            if node.operator == "+":
                result = left + right
            elif node.operator == "-":
                result = left - right
            elif node.operator == "*":
                result = left * right
            elif node.operator == "/":
                if right == 0:
                    raise EvaluationError("Divisao por zero", node.position)
                result = left / right
            else:
                raise EvaluationError("Operador binario desconhecido", node.position)
        except OverflowError as error:
            raise EvaluationError("Resultado excede o limite suportado", node.position) from error
        if isinstance(result, float) and not math.isfinite(result):
            raise EvaluationError("Resultado excede o limite suportado", node.position)
        return result
    raise TypeError("No de AST desconhecido")


def execute(
    statement: Statement, variables: MutableMapping[str, int | float]
) -> int | float | None:
    if isinstance(statement, CreateStatement):
        if statement.name in variables:
            raise EvaluationError(
                f"Variavel '{statement.name}' ja foi criada", statement.position
            )
        variables[statement.name] = evaluate(statement.expression, variables)
        return None
    if isinstance(statement, AssignmentStatement):
        if statement.name not in variables:
            raise EvaluationError(
                f"Variavel '{statement.name}' nao foi criada", statement.position
            )
        variables[statement.name] = evaluate(statement.expression, variables)
        return None
    if isinstance(statement, (ExpressionStatement, ShowStatement)):
        return evaluate(statement.expression, variables)
    raise TypeError("Comando desconhecido")