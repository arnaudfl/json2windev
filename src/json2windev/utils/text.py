def ensure_trailing_newline(s: str) -> str:
    return s if s.endswith('\n') else s + '\n'
