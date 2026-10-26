import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from cminusminus.errors import EvaluationError
from cminusminus.repl import format_result, main, repl, run_file


class ReplTests(unittest.TestCase):
    def test_repl_recovers_after_errors(self):
        output = io.StringIO()
        with patch(
            "builtins.input",
            side_effect=["", "1 +", "8 / 0", "cria total = 2 + 3 * 4", "mostrar(total)", "sair"],
        ):
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

    def test_file_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "programa.cmm"
            path.write_text(
                "cria total = 2 + 3 * 4\n"
                "mostrar(total)\n"
                "total = total + 6\n"
                "mostrar(total)\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, "-m", "cminusminus", "--file", str(path)],
                capture_output=True,
                text=True,
                cwd=Path(__file__).resolve().parents[1],
                timeout=10,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "14\n20\n")

    def test_file_syntax_error_prevents_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "programa.cmm"
            path.write_text("mostrar(2 + 3)\nmostrar(\n", encoding="utf-8")
            output = io.StringIO()
            errors = io.StringIO()
            with redirect_stdout(output), redirect_stderr(errors):
                self.assertEqual(run_file(path), 1)
            self.assertEqual(output.getvalue(), "")
            self.assertIn(f"{path}:2:", errors.getvalue())
            self.assertIn("Esperado um numero", errors.getvalue())

    def test_file_runtime_error_has_line_number(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "programa.cmm"
            path.write_text("2 + 3\n1 / 0\n4 + 5\n", encoding="utf-8")
            output = io.StringIO()
            errors = io.StringIO()
            with redirect_stdout(output), redirect_stderr(errors):
                self.assertEqual(run_file(path), 1)
            self.assertEqual(output.getvalue(), "5\n")
            self.assertIn(f"{path}:2:", errors.getvalue())
            self.assertIn("Divisao por zero", errors.getvalue())

    def test_file_not_found(self):
        errors = io.StringIO()
        with redirect_stderr(errors):
            self.assertEqual(run_file(Path("arquivo-inexistente.cmm")), 1)
        self.assertIn("Erro ao ler arquivo", errors.getvalue())

    def test_file_with_utf8_bom(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "programa.cmm"
            path.write_text("mostrar(2 + 3)\n", encoding="utf-8-sig")
            result = subprocess.run(
                [sys.executable, "-m", "cminusminus", "--file", str(path)],
                capture_output=True,
                text=True,
                cwd=Path(__file__).resolve().parents[1],
                timeout=10,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "5\n")

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