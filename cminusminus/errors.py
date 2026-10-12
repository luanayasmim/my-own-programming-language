class LanguageError(Exception):
    def __init__(self, message: str, position: int | None = None):
        self.message = message
        self.position = position
        suffix = f" (coluna {position + 1})" if position is not None else ""
        super().__init__(message + suffix)


class LexerError(LanguageError):
    pass


class ParserError(LanguageError):
    pass


class EvaluationError(LanguageError):
    pass