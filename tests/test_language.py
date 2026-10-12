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
        for source in ("abc", "2 @ 3", "1,5", ".5", "1.", "1.2.3", "1e3", "\u0661"):
            with self.subTest(source=source):
                with self.assertRaises(LexerError):
                    run_expression(source)

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


if __name__ == "__main__":
    unittest.main()