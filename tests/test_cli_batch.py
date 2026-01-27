from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "json2windev", *args],
        capture_output=True,
        text=True,
    )


def test_cli_batch_generates_outputs(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]
    in_dir = repo / "tests" / "fixtures" / "batch"
    out_dir = tmp_path / "out"

    r = run_cli([str(in_dir), "--output-dir", str(out_dir), "--format", "windev", "--continue-on-error"])
    # broken.json should cause exit code 2 (FAIL>0) if you keep that behavior.
    # If you prefer 0 even with fails, adjust accordingly.
    assert r.returncode in (0, 2)

    # ok.json should be generated
    assert (out_dir / "ok.txt").exists()

    # in markdown mode
    out_dir2 = tmp_path / "out2"
    r2 = run_cli([str(in_dir), "--output-dir", str(out_dir2), "--format", "markdown", "--continue-on-error"])
    assert r2.returncode in (0, 2)
    assert (out_dir2 / "ok.md").exists()
