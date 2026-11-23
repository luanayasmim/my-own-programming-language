from collections.abc import MutableMapping
import math

from .ast_nodes import (
    AssignmentStatement,
    BinaryOperation,
    BlockStatement,
    CreateStatement,
    ExpressionStatement,
    IfStatement,
    Node,
    Number,
    ShowStatement,
    StringLiteral,
    Statement,
    UnaryOperation,
    Value,
    Variable,
    WhileStatement,
)
from .errors import EvaluationError


def evaluate(node: Node, variables: MutableMapping[str, Value] | None = None) -> Value:
    if isinstance(node, Number):
        return node.value
    if isinstance(node, StringLiteral):
        return node.value
    if isinstance(node, Variable):
        if variables is None or node.name not in variables:
            raise EvaluationError(f"Variavel '{node.name}' nao foi criada", node.position)
        return variables[node.name]
    if isinstance(node, UnaryOperation):
        value = evaluate(node.operand, variables)
        if isinstance(value, str):
            raise EvaluationError("Operador unario requer um valor numerico", node.position)
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
                if isinstance(left, str) or isinstance(right, str):
                    try:
                        return str(left) + str(right)
                    except ValueError as error:
                        raise EvaluationError(
                            "Valor excede o limite para concatenacao", node.position
                        ) from error
                result = left + right
            elif node.operator in ("-", "*", "/"):
                if isinstance(left, str) or isinstance(right, str):
                    raise EvaluationError(
                        f"Operador '{node.operator}' requer valores numericos", node.position
                    )
                if node.operator == "-":
                    result = left - right
                elif node.operator == "*":
                    result = left * right
                else:
                    if right == 0:
                        raise EvaluationError("Divisao por zero", node.position)
                    result = left / right

            elif node.operator in ("==", "!=", "<", "<=", ">", ">="):
                if node.operator == "==":
                    result = 1 if left == right else 0
                elif node.operator == "!=":
                    result = 1 if left != right else 0
                elif node.operator == "<":
                    result = 1 if left < right else 0
                elif node.operator == "<=":
                    result = 1 if left <= right else 0
                elif node.operator == ">":
                    result = 1 if left > right else 0
                elif node.operator == ">=":
                    result = 1 if left >= right else 0
            else:
                raise EvaluationError("Operador binario desconhecido", node.position)
        except OverflowError as error:
            raise EvaluationError("Resultado excede o limite suportado", node.position) from error
        if isinstance(result, float) and not math.isfinite(result):
            raise EvaluationError("Resultado excede o limite suportado", node.position)
        return result
    raise TypeError("No de AST desconhecido")


def execute(
    statement: Statement,
    variables: MutableMapping[str, Value],
    on_output=None,
) -> Value | None:
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
        result = evaluate(statement.expression, variables)
        if on_output is not None:
            on_output(result)
        return result
    if isinstance(statement, IfStatement):
        condicao_valor = evaluate(statement.condition, variables)
        if isinstance(condicao_valor, (int, float)) and condicao_valor != 0:
            return execute(statement.consequent, variables, on_output)
        if statement.alternative is not None:
            return execute(statement.alternative, variables, on_output)
        return None
    if isinstance(statement, BlockStatement):
        last_result = None
        for child in statement.statements:
            result = execute(child, variables, on_output)
            if result is not None:
                last_result = result
        return last_result
    if isinstance(statement, WhileStatement):
        condicao_valor = evaluate(statement.condition, variables)
        repetitions = 0
        while isinstance(condicao_valor, (int, float)) and condicao_valor != 0:
            repetitions += 1
            if repetitions > 10000:
                raise EvaluationError(
                    "Limite de repeticoes do enquanto excedido", statement.position
                )
            execute(statement.body, variables, on_output)
            condicao_valor = evaluate(statement.condition, variables)
        return None
    raise TypeError("Comando desconhecido")