import io
from pathlib import Path
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from cminusminus.errors import EvaluationError
from cminusminus.repl import format_result, main, repl


class ReplTests(unittest.TestCase):
    def test_repl_recovers_after_errors(self):
        output = io.StringIO()
        with patch("builtins.input", side_effect=["", "1 +", "8 / 0", "2 + 3 * 4", "sair"]):
            with redirect_stdout(output):
                repl()
        self.assertIn("Esperado um numero", output.getvalue())
        self.assertIn("Divisao por zero", output.getvalue())
        self.assertIn("\n14\n", output.getvalue())
        self.assertIn("^", output.getvalue())

    def test_eof_and_keyboard_interrupt(self):
        for error in (EOFError, KeyboardInterrupt):
            with self.subTest(error=error):
                with patch("builtins.input", side_effect=error):
                    with redirect_stdout(io.StringIO()):
                        repl()

    def test_cli_expression(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["(2 + 3) * 4"]), 0)
        self.assertEqual(output.getvalue(), "20\n")

    def test_cli_error_exit_code(self):
        output = io.StringIO()
        with redirect_stderr(output):
            self.assertEqual(main(["1 / 0"]), 1)
        self.assertIn("Divisao por zero", output.getvalue())

    def test_negative_cli_expression(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--", "-2 + 3"]), 0)
        self.assertEqual(output.getvalue(), "1\n")

    def test_large_result_display(self):
        limit = sys.get_int_max_str_digits()
        if limit == 0:
            self.skipTest("Limite de conversao de inteiros desativado")
        with self.assertRaises(EvaluationError):
            format_result(10 ** limit)

    def test_terminal_session(self):
        result = subprocess.run(
            [sys.executable, "-m", "cminusminus"],
            input="2 + 3 * 4\n1 / 0\n(2 + 3) * 4\nsair\n",
            capture_output=True,
            text=True,
            cwd=Path(__file__).resolve().parents[1],
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("c--> 14", result.stdout)
        self.assertIn("Divisao por zero", result.stdout)
        self.assertIn("c--> 20", result.stdout)


if __name__ == "__main__":
    unittest.main()