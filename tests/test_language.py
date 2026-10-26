import unittest

from cminusminus import run_expression
from cminusminus.ast_nodes import BinaryOperation, Number
from cminusminus.errors import EvaluationError, LexerError, ParserError
from cminusminus.lexer import tokenize
from cminusminus.parser import parse


class LanguageTests(unittest.TestCase):
    def test_arithmetic(self):
        examples = {
            "42": 42,
            "2 + 3": 5,
            "10 - 4": 6,
            "3 * 4": 12,
            "10 / 4": 2.5,
            "2 + 3 * 4": 14,
            "(2 + 3) * 4": 20,
            "10 - 3 - 2": 5,
            "20 / 2 / 5": 2.0,
            "8 / 2 * 3": 12.0,
            "-5": -5,
            "+3": 3,
            "-(2 + 4)": -6,
            "2 * -3": -6,
            "2--3": 5,
            "--5": 5,
            "1.5 + 2.25": 3.75,
            " \t2 + 3\n": 5,
            "((2 + 3) * (4 - 1))": 15,
        }
        for source, expected in examples.items():
            with self.subTest(source=source):
                self.assertEqual(run_expression(source), expected)

    def test_ast_precedence(self):
        self.assertEqual(
            parse("2 + 3 * 4"),
            BinaryOperation(Number(2), "+", BinaryOperation(Number(3), "*", Number(4), 6), 2),
        )

    def test_token_positions(self):
        tokens = tokenize(" 12.5 + 2")
        self.assertEqual([token.kind for token in tokens], ["NUMBER", "+", "NUMBER", "EOF"])
        self.assertEqual([token.position for token in tokens], [1, 6, 8, 9])

    def test_invalid_syntax(self):
        for source in ("", " ", "1 +", "* 2", "()", "(2 + 3", "2 + 3)", "2 3", "2(3)", "2 ** 3", "2 // 3"):
            with self.subTest(source=source):
                with self.assertRaises(ParserError):
                    run_expression(source)

    def test_invalid_characters(self):
        for source in ("2 @ 3", "1,5", ".5", "1.", "1.2.3", "\u0661"):
            with self.subTest(source=source):
                with self.assertRaises(LexerError):
                    run_expression(source)

    def test_undeclared_variable_in_expression(self):
        with self.assertRaisesRegex(EvaluationError, "nao foi criada"):
            run_expression("abc")

    def test_scientific_notation_is_not_supported(self):
        with self.assertRaises(ParserError):
            run_expression("1e3")

    def test_division_by_zero(self):
        for source in ("8 / 0", "1 / (2 - 2)", "1 / -0.0"):
            with self.subTest(source=source):
                with self.assertRaisesRegex(EvaluationError, "Divisao por zero"):
                    run_expression(source)

    def test_error_position(self):
        with self.assertRaises(LexerError) as context:
            run_expression("2 + @")
        self.assertEqual(context.exception.position, 4)
        self.assertIn("coluna 5", str(context.exception))

    def test_float_limits(self):
        with self.assertRaises(ParserError):
            run_expression("9" * 400 + ".0")
        with self.assertRaises(EvaluationError):
            run_expression("1" + "0" * 200 + ".0 * 1" + "0" * 200 + ".0")

    def test_depth_limit(self):
        with self.assertRaises(EvaluationError):
            run_expression("(" * 2000 + "1" + ")" * 2000)

    def test_variables_and_statements(self):
        from cminusminus import compile_statement, run_statement

        variables = {}
        self.assertIsNone(run_statement("cria total = 2 + 3 * 4", variables))
        self.assertEqual(run_statement("mostrar(total)", variables), 14)
        self.assertIsNone(run_statement("total = total + 6", variables))
        self.assertEqual(run_statement("total", variables), 20)
        self.assertEqual(
            compile_statement("cria numero = 3").__class__.__name__,
            "CreateStatement",
        )

    def test_variable_errors(self):
        from cminusminus import run_statement

        variables = {}
        with self.assertRaisesRegex(EvaluationError, "nao foi criada"):
            run_statement("valor = 2", variables)
        run_statement("cria valor = 2", variables)
        with self.assertRaisesRegex(EvaluationError, "ja foi criada"):
            run_statement("cria valor = 3", variables)

    def test_statement_syntax_errors(self):
        from cminusminus import compile_statement

        for source in ("cria = 2", "cria x 2", "mostrar()", "mostrar(2", "x ="):
            with self.subTest(source=source), self.assertRaises(ParserError):
                compile_statement(source)

    def test_identifiers_are_tokenized(self):
        self.assertEqual(
            [token.kind for token in tokenize("cria resultado = valor_2")],
            ["CREATE", "IDENTIFIER", "=", "IDENTIFIER", "EOF"],
        )


if __name__ == "__main__":
    unittest.main()