from .errors import EvaluationError, LanguageError
from .evaluator import evaluate
from .parser import parse

__all__ = ["LanguageError", "run_expression"]


def run_expression(source: str) -> int | float:
    try:
        return evaluate(parse(source))
    except RecursionError as error:
        raise EvaluationError("Expressao excede o limite de profundidade") from error