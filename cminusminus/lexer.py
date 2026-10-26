from dataclasses import dataclass

from .errors import LexerError


@dataclass(frozen=True)
class Token:
    kind: str
    text: str
    position: int


def tokenize(source: str) -> list[Token]:
    tokens: list[Token] = []
    position = 0
    while position < len(source):
        character = source[position]
        if character.isspace():
            position += 1
            continue
        if character in "+-*/()=":
            tokens.append(Token(character, character, position))
            position += 1
            continue
        if character.isascii() and (character.isalpha() or character == "_"):
            start = position
            position += 1
            while position < len(source) and source[position].isascii() and (
                source[position].isalnum() or source[position] == "_"
            ):
                position += 1
            text = source[start:position]
            kind = {"cria": "CREATE", "mostrar": "SHOW"}.get(text, "IDENTIFIER")
            tokens.append(Token(kind, text, start))
            continue
        if character in "0123456789":
            start = position
            while position < len(source) and source[position] in "0123456789":
                position += 1
            if position < len(source) and source[position] == ".":
                position += 1
                decimal_start = position
                while position < len(source) and source[position] in "0123456789":
                    position += 1
                if position == decimal_start:
                    raise LexerError("Esperado um digito depois do ponto decimal", position)
            tokens.append(Token("NUMBER", source[start:position], start))
            continue
        raise LexerError(f"Caractere invalido: {character!r}", position)
    tokens.append(Token("EOF", "", len(source)))
    return tokens