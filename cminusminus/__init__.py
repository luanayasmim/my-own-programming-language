from .errors import EvaluationError, LanguageError
from .ast_nodes import Node
from .evaluator import evaluate
from .parser import parse

__all__ = ["LanguageError", "compile_expression", "run_expression"]


def compile_expression(source: str) -> Node:
    try:
        return parse(source)
    except RecursionError as error:
        raise EvaluationError("Expressao excede o limite de profundidade") from error


def run_expression(source: str) -> int | float:
    try:
        return evaluate(compile_expression(source))
    except RecursionError as error:
        raise EvaluationError("Expressao excede o limite de profundidade") from error