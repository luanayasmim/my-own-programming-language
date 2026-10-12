import math

from .ast_nodes import BinaryOperation, Node, Number, UnaryOperation
from .errors import EvaluationError


def evaluate(node: Node) -> int | float:
    if isinstance(node, Number):
        return node.value
    if isinstance(node, UnaryOperation):
        value = evaluate(node.operand)
        if node.operator == "+":
            return value
        if node.operator == "-":
            return -value
        raise EvaluationError("Operador unario desconhecido", node.position)
    if isinstance(node, BinaryOperation):
        left = evaluate(node.left)
        right = evaluate(node.right)
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