from __future__ import annotations

import argparse
import sys
from pathlib import Path

from json2windev.rules.loader import load_rules
from json2windev.renderers.windev import WinDevRenderer
from json2windev.core.infer import infer_schema
from json2windev.core.input import parse_json, pretty_json, JsonParseError


def _read_input(path: str) -> str:
    if path != "-":
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def _write_output(path: str, content: str) -> None:
    if path == "-":
        sys.stdout.write(content)
    else:
        Path(path).write_text(content, encoding="utf-8")


def _default_ext(fmt: str) -> str:
    return ".md" if fmt == "markdown" else ".txt"


def _render_one(json_text: str, rules, fmt: str) -> str:
    data = parse_json(json_text)
    schema = infer_schema(data)

    if fmt == "windev":
        renderer = WinDevRenderer(rules)
        return renderer.render(schema)

    if fmt == "markdown":
        from json2windev.renderers.markdown import MarkdownRenderer
        renderer = MarkdownRenderer(rules)
        return renderer.render(schema)

    raise ValueError(f"Unsupported format: {fmt}")


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

    p.add_argument("--validate-only", action="store_true", help="Validate JSON and infer schema, then exit")
    p.add_argument("--pretty", action="store_true", help="Pretty-print the input JSON (after parsing) and exit")

    p.add_argument("--output-dir", default=None, help="Output directory for batch mode (when input is a directory)")
    p.add_argument("--continue-on-error", action="store_true", help="Continue processing other files on error (batch mode)")

    args = p.parse_args(argv)

    if args.gui:
        from json2windev.app.gui_tk import run_gui
        run_gui()
        return

    try:
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

        input_path = Path(args.input)

        # ===== BATCH MODE =====
        if input_path.exists() and input_path.is_dir():
            if not args.output_dir:
                print("ERROR: --output-dir is required when input is a directory.", file=sys.stderr)
                raise SystemExit(2)

            out_dir = Path(args.output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)

            json_files = sorted(input_path.rglob("*.json"))
            if not json_files:
                print(f"ERROR: No .json files found in directory: {input_path}", file=sys.stderr)
                raise SystemExit(2)

            ok = 0
            failed = 0

            for f in json_files:
                try:
                    json_text = f.read_text(encoding="utf-8")
                    rendered = _render_one(json_text, rules, args.format)

                    rel = f.relative_to(input_path)
                    target = (out_dir / rel).with_suffix(_default_ext(args.format))
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(rendered, encoding="utf-8")

                    ok += 1
                    print(f"[OK] {rel}")

                except Exception as e:
                    failed += 1
                    print(f"[FAIL] {f}: {e}", file=sys.stderr)
                    if not args.continue_on_error:
                        raise SystemExit(2)

            print(f"Done. OK={ok}, FAIL={failed}")
            return

        # Pipeline (explicit, format-ready)
        json_text = _read_input(args.input)
        data = parse_json(json_text)

        if args.pretty:
            _write_output(args.output, pretty_json(data))
            return

        schema = infer_schema(data)

        if args.validate_only:
            # If we reached here, JSON was valid and schema inference succeeded
            _write_output(args.output, "OK\n")
            return

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

    except JsonParseError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(2)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
