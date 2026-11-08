"""Fail if a tracked file contains a private-key block."""

from __future__ import annotations

from pathlib import Path

SKIP = {
    ".git",
    ".venv",
    "dist",
    "build",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}
MARKERS = (
    b"BEGIN PRIVATE KEY",
    b"BEGIN RSA PRIVATE KEY",
    b"BEGIN OPENSSH PRIVATE KEY",
)


def main() -> None:
    bad: list[str] = []
    for path in Path(".").rglob("*"):
        if not path.is_file() or SKIP.intersection(path.parts):
            continue
        blob = path.read_bytes()
        if any(marker in blob for marker in MARKERS):
            bad.append(str(path))
    if bad:
        raise SystemExit("\n".join(bad))


if __name__ == "__main__":
    main()
