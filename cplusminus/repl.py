import argparse
from pathlib import Path
import sys

from . import (
    compile_program,
    compile_statement,
    run_expression,
    run_program,
    run_statement,
)
from .evaluator import execute
from .lexer import tokenize
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

    for line_number, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            tokens = tokenize(stripped)
            if tokens[0].kind not in ("WHILE", "END_WHILE"):
                compile_statement(stripped)
        except LanguageError as error:
            detail = format_error(stripped, error)
            print(
                f"Erro: {path}:{line_number}: {detail.removeprefix('Erro: ')}",
                file=sys.stderr,
            )
            return 1
    try:
        compile_program(source)
    except LanguageError as error:
        print(f"Erro: {path}:1: {error}", file=sys.stderr)
        return 1

    variables: dict[str, Value] = {}
    try:
        execute(
            compile_program(source),
            variables,
            lambda result: print(format_result(result)),
        )
    except LanguageError as error:
        runtime_line = 1
        if "Divisao por zero" in str(error):
            for line_number, line in enumerate(source.splitlines(), start=1):
                if "/" in line:
                    runtime_line = line_number
                    break
        elif error.position is not None:
            for line_number, line in enumerate(source.splitlines(), start=1):
                try:
                    tokens = tokenize(line.strip())
                except LanguageError:
                    continue
                if any(token.position == error.position for token in tokens):
                    runtime_line = line_number
                    break
        print(f"Erro: {path}:{runtime_line}: {error}", file=sys.stderr)
        return 1
    except RecursionError:
        error = EvaluationError("Expressao excede o limite de profundidade")
        print(f"Erro: {path}:1: {error}", file=sys.stderr)
        return 1
    return 0


def repl() -> None:
    print("cplusminus")
    variables: dict[str, Value] = {}
    pending_lines: list[str] = []
    while_depth = 0
    while True:
        try:
            source = input("c+-> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if source.strip().lower() == "sair":
            return
        if not source.strip():
            continue

        if pending_lines:
            pending_lines.append(source)
            try:
                first_kind = tokenize(source.strip())[0].kind
            except LanguageError:
                first_kind = None
            if first_kind == "WHILE":
                while_depth += 1
            elif first_kind == "END_WHILE":
                while_depth -= 1
            if while_depth > 0:
                continue
            source = "\n".join(pending_lines)
            pending_lines = []
        else:
            try:
                first_kind = tokenize(source.strip())[0].kind
            except LanguageError:
                first_kind = None
            if first_kind == "WHILE":
                pending_lines = [source]
                while_depth = 1
                continue

        try:
            if "\n" in source or first_kind in ("WHILE", "END_WHILE"):
                for result in run_program(source, variables):
                    print(format_result(result))
            else:
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
        prog="cplusminus", description="Interpretador de calculos matematicos simples."
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