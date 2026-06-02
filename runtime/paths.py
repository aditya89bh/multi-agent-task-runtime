"""File path safety helpers for local runtime tooling."""

from __future__ import annotations

from pathlib import Path


def ensure_input_file(path: str | Path, label: str = "input") -> Path:
    resolved = Path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"{label} path does not exist: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"{label} path must be a file: {resolved}")
    return resolved


def ensure_output_file(path: str | Path, label: str = "output") -> Path:
    resolved = Path(path)
    if resolved.exists() and resolved.is_dir():
        raise ValueError(f"{label} path must be a file, not a directory: {resolved}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved
