import argparse
from pathlib import Path
import sys

from . import compile_statement, run_expression, run_statement
from .ast_nodes import Statement, Value
from .errors import EvaluationError, LanguageError


def format_result(value: Value) -> str:
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
        source = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        print(f"Erro ao ler arquivo '{path}': {error}", file=sys.stderr)
        return 1

    statements: list[tuple[int, str, Statement]] = []
    for line_number, line in enumerate(source.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            statements.append((line_number, line, compile_statement(line)))
        except LanguageError as error:
            detail = format_error(line, error)
            print(f"Erro: {path}:{line_number}: {detail.removeprefix('Erro: ')}", file=sys.stderr)
            return 1

    variables: dict[str, Value] = {}
    for line_number, line, statement in statements:
        try:
            result = run_statement(line, variables)
            if result is not None:
                print(format_result(result))
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
    variables: dict[str, Value] = {}
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
            result = run_statement(source, variables)
            if result is not None:
                print(format_result(result))
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