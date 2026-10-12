import argparse
import sys

from . import run_expression
from .errors import EvaluationError, LanguageError


def format_result(value: int | float) -> str:
    try:
        return str(value)
    except ValueError as error:
        raise EvaluationError("Resultado excede o limite de exibicao") from error


def format_error(source: str, error: LanguageError) -> str:
    message = f"Erro: {error}"
    if error.position is None:
        return message
    return f"{message}\n{source}\n{' ' * error.position}^"


def repl() -> None:
    print("cminusminus")
    while True:
        try:
            source = input("c--> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if source.strip().lower() == "sair":
            return
        if not source.strip():
            continue
        try:
            print(format_result(run_expression(source)))
        except LanguageError as error:
            print(format_error(source, error))
        except KeyboardInterrupt:
            print()
            return


def main(argv: list[str] | None = None) -> int:
    argument_parser = argparse.ArgumentParser(
        prog="cminusminus", description="Interpretador de calculos matematicos simples."
    )
    argument_parser.add_argument("expression", nargs="?", help="expressao matematica")
    arguments = argument_parser.parse_args(argv)
    if arguments.expression is None:
        repl()
        return 0
    try:
        print(format_result(run_expression(arguments.expression)))
    except LanguageError as error:
        print(format_error(arguments.expression, error), file=sys.stderr)
        return 1
    return 0