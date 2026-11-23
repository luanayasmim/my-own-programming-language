from .errors import EvaluationError, LanguageError
from .ast_nodes import BlockStatement, Node, Statement, Value, WhileStatement
from .evaluator import evaluate, execute
from .parser import parse, parse_statement
from .lexer import tokenize
from .errors import ParserError

__all__ = [
    "LanguageError",
    "compile_expression",
    "compile_statement",
    "compile_program",
    "run_expression",
    "run_statement",
    "run_program",
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


def compile_program(source: str) -> BlockStatement:
    def compile_block(
        lines: list[str], start: int = 0, allow_end: bool = False
    ) -> tuple[BlockStatement, int]:
        statements: list[Statement] = []
        index = start
        while index < len(lines):
            line = lines[index]
            stripped = line.strip()
            if not stripped:
                index += 1
                continue

            tokens = tokenize(stripped)
            if tokens[0].kind == "END_WHILE":
                if not allow_end:
                    raise ParserError(
                        "fim_enquanto sem enquanto correspondente",
                        tokens[0].position,
                    )
                if tokens[1].kind != "EOF":
                    raise ParserError(
                        "fim_enquanto nao aceita argumentos", tokens[1].position
                    )
                return BlockStatement(tuple(statements)), index

            if tokens[0].kind == "WHILE":
                condition_text = stripped[len("enquanto"):].strip()
                if not condition_text:
                    raise ParserError(
                        "Esperado uma condicao depois de 'enquanto'",
                        tokens[0].position,
                    )
                condition = parse(condition_text)
                body, end_index = compile_block(lines, index + 1, True)
                if end_index >= len(lines):
                    raise ParserError(
                        "Esperado 'fim_enquanto'",
                        tokens[0].position,
                    )
                statements.append(
                    WhileStatement(condition, body, tokens[0].position)
                )
                index = end_index + 1
                continue

            statements.append(parse_statement(stripped))
            index += 1

        return BlockStatement(tuple(statements)), len(lines)

    block, _ = compile_block(source.splitlines())
    return block


def run_program(
    source: str, variables: dict[str, Value]
) -> list[Value]:
    outputs: list[Value] = []
    execute(compile_program(source), variables, outputs.append)
    return outputs


def run_expression(source: str) -> Value:
    try:
        return evaluate(compile_expression(source))
    except RecursionError as error:
        raise EvaluationError("Expressao excede o limite de profundidade") from error