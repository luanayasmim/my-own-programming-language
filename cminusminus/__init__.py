from .errors import EvaluationError, LanguageError
from .ast_nodes import Node, Statement, Value
from .evaluator import evaluate, execute
from .parser import parse, parse_statement

__all__ = [
    "LanguageError",
    "compile_expression",
    "compile_statement",
    "run_expression",
    "run_statement",
]


def compile_expression(source: str) -> Node:
    try:
        return parse(source)
    except RecursionError as error:
        raise EvaluationError("Expressao excede o limite de profundidade") from error


def compile_statement(source: str) -> Statement:
    try:
        return parse_statement(source)
    except RecursionError as error:
        raise EvaluationError("Comando excede o limite de profundidade") from error


def run_statement(source: str, variables: dict[str, Value]) -> Value | None:
    try:
        return execute(compile_statement(source), variables)
    except RecursionError as error:
        raise EvaluationError("Comando excede o limite de profundidade") from error


def run_expression(source: str) -> Value:
    try:
        return evaluate(compile_expression(source))
    except RecursionError as error:
        raise EvaluationError("Expressao excede o limite de profundidade") from error