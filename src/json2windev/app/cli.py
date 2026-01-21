from __future__ import annotations
import argparse
import sys
from pathlib import Path
from json2windev import generate_windev_from_json

def _read_input(path: str) -> str:
    if path != "-":
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()

def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="json2windev", description="Generate WinDev structures from JSON")
    p.add_argument("input", nargs="?", default="-", help="Input JSON file, or '-' for stdin")
    p.add_argument("--rules", default="config/windev_rules.yaml", help="Path to rules YAML")
    p.add_argument("-o","--output", default="-", help="Output file path, or '-' for stdout")
    args = p.parse_args(argv)

    try:
        json_text = _read_input(args.input)
        out = generate_windev_from_json(json_text, args.rules)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(2)

    if args.output == "-":
        sys.stdout.write(out)
    else:
        Path(args.output).write_text(out, encoding="utf-8")

if __name__ == "__main__":
    main()
