import argparse
from pathlib import Path
import sys

from . import compile_expression, run_expression
from .ast_nodes import Node
from .errors import EvaluationError, LanguageError
from .evaluator import evaluate


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


def run_file(path: Path) -> int:
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(f"Erro ao ler arquivo '{path}': {error}", file=sys.stderr)
        return 1

    expressions: list[tuple[int, str, Node]] = []
    for line_number, line in enumerate(source.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            expressions.append((line_number, line, compile_expression(line)))
        except LanguageError as error:
            detail = format_error(line, error)
            print(f"Erro: {path}:{line_number}: {detail.removeprefix('Erro: ')}", file=sys.stderr)
            return 1

    for line_number, line, expression in expressions:
        try:
            print(format_result(evaluate(expression)))
        except LanguageError as error:
            detail = format_error(line, error)
            print(f"Erro: {path}:{line_number}: {detail.removeprefix('Erro: ')}", file=sys.stderr)
            return 1
        except RecursionError:
            error = EvaluationError("Expressao excede o limite de profundidade")
            print(f"Erro: {path}:{line_number}: {error}", file=sys.stderr)
            return 1
    return 0


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
    argument_parser.add_argument("--file", type=Path, help="arquivo com uma expressao por linha")
    arguments = argument_parser.parse_args(argv)
    if arguments.expression is not None and arguments.file is not None:
        argument_parser.error("informe uma expressao ou --file, nao ambos")
    if arguments.file is not None:
        return run_file(arguments.file)
    if arguments.expression is None:
        repl()
        return 0
    try:
        print(format_result(run_expression(arguments.expression)))
    except LanguageError as error:
        print(format_error(arguments.expression, error), file=sys.stderr)
        return 1
    return 0