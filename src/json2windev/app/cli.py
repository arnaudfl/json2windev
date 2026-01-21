from __future__ import annotations

import argparse
import sys
from pathlib import Path

from json2windev import generate_windev_from_json
from json2windev.rules.loader import load_rules
from json2windev.renderers.windev import WinDevRenderer
from json2windev.core.infer import parse_json, infer_schema


def _read_input(path: str) -> str:
    if path != "-":
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def _write_output(path: str, content: str) -> None:
    if path == "-":
        sys.stdout.write(content)
    else:
        Path(path).write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(
        prog="json2windev",
        description="Generate WinDev structures from JSON (prefixes + <serialize> supported).",
    )

    p.add_argument("input", nargs="?", default="-", help="Input JSON file path, or '-' for stdin")
    p.add_argument("--rules", default="config/windev_rules.yaml", help="Path to windev rules YAML")
    p.add_argument("-o", "--output", default="-", help="Output file path, or '-' for stdout")

    p.add_argument("--format", default="windev", choices=["windev", "markdown"], help="Output format")
    p.add_argument("--no-prefixes", action="store_true", help="Disable WinDev variable prefixes (runtime override)")
    p.add_argument("--no-serialize", action="store_true", help="Disable <serialize=\"...\"> (runtime override)")
    p.add_argument("--print-rules", action="store_true", help="Print effective rules (after overrides) and exit")
    p.add_argument("--gui", action="store_true", help="Launch the GUI (Tkinter)")

    args = p.parse_args(argv)

    if args.gui:
        from json2windev.app.gui_tk import run_gui
        run_gui()
        return

    try:
        json_text = _read_input(args.input)

        # Load rules + apply runtime overrides
        rules = load_rules(args.rules)

        # Small runtime overrides without touching YAML
        if args.no_prefixes:
            rules.raw["naming"]["use_variable_prefixes"] = False
        if args.no_serialize:
            rules.raw["naming"]["serialize_attribute"] = False

        if args.print_rules:
            import yaml
            _write_output(args.output, yaml.safe_dump(rules.raw, sort_keys=False, allow_unicode=True))
            return

        # Pipeline (explicit, format-ready)
        data = parse_json(json_text)
        schema = infer_schema(data)

        if args.format == "windev":
            renderer = WinDevRenderer(rules)
            out = renderer.render(schema)
        elif args.format == "markdown":
            from json2windev.renderers.markdown import MarkdownRenderer
            renderer = MarkdownRenderer(rules)
            out = renderer.render(schema)
        else:
            raise ValueError(f"Unsupported format: {args.format}")

        _write_output(args.output, out)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
