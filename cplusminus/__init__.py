from .errors import EvaluationError, LanguageError
from .ast_nodes import BlockStatement, IfStatement, Node, Statement, Value, WhileStatement
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
        lines: list[str],
        start: int = 0,
        allowed_markers: set[str] | None = None,
    ) -> tuple[BlockStatement, int, str | None]:
        allowed_markers = allowed_markers or set()
        statements: list[Statement] = []
        index = start
        while index < len(lines):
            line = lines[index]
            stripped = line.strip()
            if not stripped:
                index += 1
                continue

            tokens = tokenize(stripped)
            marker = tokens[0].kind
            if marker in ("END_WHILE", "ELSE", "END_IF"):
                if marker not in allowed_markers:
                    if marker == "END_WHILE":
                        raise ParserError("fim_enquanto sem enquanto correspondente", tokens[0].position)
                    if marker == "ELSE":
                        raise ParserError("senao sem se correspondente", tokens[0].position)
                    raise ParserError("fim_se sem se correspondente", tokens[0].position)
                if marker == "END_WHILE" and tokens[1].kind != "EOF":
                    raise ParserError("fim_enquanto nao aceita argumentos", tokens[1].position)
                if marker == "ELSE" and tokens[1].kind != "EOF":
                    raise ParserError("senao nao aceita argumentos", tokens[1].position)
                if marker == "END_IF" and tokens[1].kind != "EOF":
                    raise ParserError("fim_se nao aceita argumentos", tokens[1].position)
                return BlockStatement(tuple(statements)), index, marker

            if tokens[0].kind == "WHILE":
                condition_text = stripped[len("enquanto"):].strip()
                if not condition_text:
                    raise ParserError(
                        "Esperado uma condicao depois de 'enquanto'",
                        tokens[0].position,
                    )
                condition = parse(condition_text)
                body, end_index, marker = compile_block(lines, index + 1, {"END_WHILE"})
                if marker != "END_WHILE":
                    raise ParserError("Esperado 'fim_enquanto'", tokens[0].position)
                statements.append(
                    WhileStatement(condition, body, tokens[0].position)
                )
                index = end_index + 1
                continue

            if tokens[0].kind == "IF":
                condition_text = stripped[len("se"):].strip()
                if not condition_text:
                    raise ParserError(
                        "Esperado uma condicao depois de 'se'",
                        tokens[0].position,
                    )
                try:
                    block_condition = parse(condition_text)
                    is_block = True
                except ParserError:
                    is_block = False

                if not is_block:
                    statements.append(parse_statement(stripped))
                    index += 1
                    continue

                consequent, end_index, marker = compile_block(
                    lines, index + 1, {"ELSE", "END_IF"}
                )
                if marker is None:
                    raise ParserError("Esperado 'fim_se'", tokens[0].position)

                alternative = None
                if marker == "ELSE":
                    alternative, end_index, marker = compile_block(
                        lines, end_index + 1, {"END_IF"}
                    )
                    if marker != "END_IF":
                        raise ParserError("Esperado 'fim_se'", tokens[0].position)

                if marker != "END_IF":
                    raise ParserError("Esperado 'fim_se'", tokens[0].position)
                statements.append(
                    IfStatement(
                        block_condition,
                        consequent,
                        tokens[0].position,
                        alternative,
                    )
                )
                index = end_index + 1
                continue

            statements.append(parse_statement(stripped))
            index += 1

        return BlockStatement(tuple(statements)), len(lines), None

    block, _, _ = compile_block(source.splitlines())
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