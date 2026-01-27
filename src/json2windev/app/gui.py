from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from json2windev.core.input import parse_json, pretty_json, JsonParseError
from json2windev.core.infer import infer_schema
from json2windev.rules.loader import load_rules, RulesError
from json2windev.renderers.windev import WinDevRenderer
from json2windev.renderers.markdown import MarkdownRenderer


class Json2WinDevGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("json2windev (GUI)")
        self.geometry("1100x750")
        self.minsize(900, 650)

        self.var_format = tk.StringVar(value="windev")
        self.var_rules = tk.StringVar(value=str(Path("config") / "windev_rules.yaml"))

        self._build_ui()

    def _build_ui(self) -> None:
        # Top bar
        top = ttk.Frame(self, padding=10)
        top.pack(fill=tk.X)

        ttk.Label(top, text="Format:").pack(side=tk.LEFT)
        fmt = ttk.Combobox(top, textvariable=self.var_format, values=["windev", "markdown"], width=10, state="readonly")
        fmt.pack(side=tk.LEFT, padx=(6, 14))

        ttk.Label(top, text="Rules file:").pack(side=tk.LEFT)
        rules_entry = ttk.Entry(top, textvariable=self.var_rules, width=55)
        rules_entry.pack(side=tk.LEFT, padx=(6, 6))

        ttk.Button(top, text="Browse…", command=self._browse_rules).pack(side=tk.LEFT, padx=(0, 14))

        ttk.Button(top, text="Validate", command=self._on_validate).pack(side=tk.LEFT)
        ttk.Button(top, text="Generate", command=self._on_generate).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(top, text="Pretty JSON", command=self._on_pretty).pack(side=tk.LEFT, padx=(14, 0))

        # Status line
        self.status = tk.StringVar(value="Ready.")
        status_bar = ttk.Label(self, textvariable=self.status, padding=(10, 6))
        status_bar.pack(fill=tk.X)

        # Main split
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Left: input
        left = ttk.Frame(paned, padding=(0, 0, 6, 0))
        paned.add(left, weight=1)

        left_top = ttk.Frame(left)
        left_top.pack(fill=tk.X)

        ttk.Label(left_top, text="Input JSON").pack(side=tk.LEFT)

        ttk.Button(left_top, text="Load JSON…", command=self._load_json).pack(side=tk.RIGHT)
        ttk.Button(left_top, text="Clear", command=self._clear_input).pack(side=tk.RIGHT, padx=(0, 6))

        in_frame = ttk.Frame(left)
        in_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        in_scroll_y = ttk.Scrollbar(in_frame, orient=tk.VERTICAL)
        in_scroll_x = ttk.Scrollbar(in_frame, orient=tk.HORIZONTAL)

        self.txt_in = tk.Text(
            in_frame,
            wrap="none",
            undo=True,
            yscrollcommand=in_scroll_y.set,
            xscrollcommand=in_scroll_x.set,
        )
        in_scroll_y.config(command=self.txt_in.yview)
        in_scroll_x.config(command=self.txt_in.xview)

        in_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        in_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.txt_in.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right: output
        right = ttk.Frame(paned, padding=(6, 0, 0, 0))
        paned.add(right, weight=1)

        right_top = ttk.Frame(right)
        right_top.pack(fill=tk.X)

        ttk.Label(right_top, text="Output").pack(side=tk.LEFT)

        ttk.Button(right_top, text="Save output…", command=self._save_output).pack(side=tk.RIGHT)
        ttk.Button(right_top, text="Copy output", command=self._copy_output).pack(side=tk.RIGHT, padx=(0, 6))
        ttk.Button(right_top, text="Clear", command=self._clear_output).pack(side=tk.RIGHT, padx=(0, 6))

        out_frame = ttk.Frame(right)
        out_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        out_scroll_y = ttk.Scrollbar(out_frame, orient=tk.VERTICAL)
        out_scroll_x = ttk.Scrollbar(out_frame, orient=tk.HORIZONTAL)

        self.txt_out = tk.Text(
            out_frame,
            wrap="none",
            yscrollcommand=out_scroll_y.set,
            xscrollcommand=out_scroll_x.set,
        )
        out_scroll_y.config(command=self.txt_out.yview)
        out_scroll_x.config(command=self.txt_out.xview)

        out_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        out_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.txt_out.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        mono = tkfont.Font(family="Consolas", size=10)
        self.txt_in.configure(font=mono)
        self.txt_out.configure(font=mono)

        # Shortcuts
        self.bind("<Control-Return>", lambda e: self._on_generate())
        self.bind("<Control-Shift-Return>", lambda e: self._on_validate())

        # Small help footer
        footer = ttk.Label(
            self,
            text="Tip: activate (.venv) then run: python -m json2windev.app.gui",
            padding=(10, 6),
        )
        footer.pack(fill=tk.X)

    # ---------- Actions

    def _browse_rules(self) -> None:
        path = filedialog.askopenfilename(
            title="Select windev_rules.yaml",
            filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")],
        )
        if path:
            self.var_rules.set(path)

    def _load_json(self) -> None:
        path = filedialog.askopenfilename(
            title="Open JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        p = Path(path)
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = p.read_text(encoding="utf-8-sig")
        self._set_input(text)
        self.status.set(f"Loaded: {p.name}")

    def _save_output(self) -> None:
        fmt = self.var_format.get()
        default_ext = ".md" if fmt == "markdown" else ".txt"

        path = filedialog.asksaveasfilename(
            title="Save output",
            defaultextension=default_ext,
            filetypes=[("Markdown", "*.md"), ("Text", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return

        out = self._get_output()
        Path(path).write_text(out, encoding="utf-8")
        self.status.set(f"Saved: {Path(path).name}")

    def _copy_output(self) -> None:
        out = self._get_output()
        self.clipboard_clear()
        self.clipboard_append(out)
        self.status.set("Output copied to clipboard.")

    def _clear_input(self) -> None:
        self.txt_in.delete("1.0", tk.END)
        self.status.set("Input cleared.")

    def _clear_output(self) -> None:
        self.txt_out.delete("1.0", tk.END)
        self.status.set("Output cleared.")

    def _on_pretty(self) -> None:
        try:
            data = parse_json(self._get_input())
            self._set_input(pretty_json(data))
            self.status.set("JSON formatted.")
        except JsonParseError as e:
            messagebox.showerror("Invalid JSON", str(e))
            self.status.set("Invalid JSON.")

    def _on_validate(self) -> None:
        try:
            rules = self._load_rules()
            _ = rules  # currently unused, but keeps parity with CLI (rules must exist)
            data = parse_json(self._get_input())
            _ = infer_schema(data)
            self.status.set("OK: JSON valid and schema inferred.")
            messagebox.showinfo("Validate", "OK: JSON valid and schema inferred.")
        except (JsonParseError, RulesError) as e:
            messagebox.showerror("Validate failed", str(e))
            self.status.set("Validate failed.")
        except Exception as e:
            messagebox.showerror("Validate failed", f"Unexpected error: {e}")
            self.status.set("Validate failed (unexpected).")

    def _on_generate(self) -> None:
        try:
            rules = self._load_rules()
            data = parse_json(self._get_input())
            schema = infer_schema(data)

            fmt = self.var_format.get()
            if fmt == "windev":
                out = WinDevRenderer(rules).render(schema)
            elif fmt == "markdown":
                out = MarkdownRenderer(rules).render(schema)
            else:
                raise ValueError(f"Unsupported format: {fmt}")

            self._set_output(out)
            self.status.set(f"Generated ({fmt}).")
        except (JsonParseError, RulesError) as e:
            messagebox.showerror("Generate failed", str(e))
            self.status.set("Generate failed.")
        except Exception as e:
            messagebox.showerror("Generate failed", f"Unexpected error: {e}")
            self.status.set("Generate failed (unexpected).")

    # ---------- Helpers

    def _load_rules(self):
        rules_path = Path(self.var_rules.get())
        return load_rules(rules_path)

    def _get_input(self) -> str:
        return self.txt_in.get("1.0", tk.END).strip()

    def _set_input(self, text: str) -> None:
        self.txt_in.delete("1.0", tk.END)
        self.txt_in.insert("1.0", text)

    def _get_output(self) -> str:
        return self.txt_out.get("1.0", tk.END).rstrip() + "\n"

    def _set_output(self, text: str) -> None:
        self.txt_out.delete("1.0", tk.END)
        self.txt_out.insert("1.0", text)


def main() -> None:
    app = Json2WinDevGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
