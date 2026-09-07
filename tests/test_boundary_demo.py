from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "boundary-demo"
INITIALIZER = SKILL / "scripts" / "init_demo.py"
TEMPLATE = SKILL / "assets" / "streamlit-boundary-demo"


class BoundaryDemoTests(unittest.TestCase):
    def test_initializer_creates_local_safe_streamlit_probe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "demo"
            result = subprocess.run(
                [
                    sys.executable,
                    str(INITIALIZER),
                    str(target),
                    "--name",
                    "Boundary \"{{QUESTION_PY}}\" Check",
                    "--question",
                    "Should {{DEMO_NAME}} remain literal\nand block the boundary?",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("Created boundary demo", result.stdout)
            config = (target / ".streamlit" / "config.toml").read_text(
                encoding="utf-8"
            )
            self.assertIn("runOnSave = true", config)
            self.assertIn('address = "127.0.0.1"', config)
            experiment = (target / "experiment.md").read_text(encoding="utf-8")
            self.assertIn(
                "Should {{DEMO_NAME}} remain literal\nand block the boundary?",
                experiment,
            )
            app_source = (target / "streamlit_app.py").read_text(encoding="utf-8")
            self.assertIn('Boundary \\"{{QUESTION_PY}}\\" Check', app_source)
            self.assertIn("Should {{DEMO_NAME}} remain literal", app_source)
            subprocess.run(
                [sys.executable, "-m", "compileall", "-q", str(target)],
                text=True,
                capture_output=True,
                check=True,
            )

    def test_initializer_refuses_a_nonempty_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "demo"
            target.mkdir()
            marker = target / "keep.txt"
            marker.write_text("preserve", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(INITIALIZER),
                    str(target),
                    "--question",
                    "Will this be refused?",
                ],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertEqual("preserve", marker.read_text(encoding="utf-8"))

    def test_template_cases_pass_the_portable_engine(self) -> None:
        code = """
from pathlib import Path
from boundary_demo.adapters import FakeAdapter
from boundary_demo.cases import load_cases
from boundary_demo.evaluation import evaluate
from boundary_demo.runner import run_case

root = Path.cwd()
for case in load_cases(root / 'cases'):
    result = run_case(case, FakeAdapter(case['given']['adapter']['scenario']))
    assert evaluate(case, result).verdict == 'pass'
"""
        subprocess.run(
            [sys.executable, "-c", code],
            cwd=TEMPLATE,
            text=True,
            capture_output=True,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
