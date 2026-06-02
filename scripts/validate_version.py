"""Validate project semantic versioning."""

from __future__ import annotations

import re
from pathlib import Path

SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def read_project_version(pyproject_path: str | Path = "pyproject.toml") -> str:
    in_project = False
    for raw_line in Path(pyproject_path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == "[project]":
            in_project = True
            continue
        if in_project and line.startswith("["):
            break
        if in_project and line.startswith("version"):
            _, value = line.split("=", 1)
            return value.strip().strip('"')
    raise ValueError("project.version is missing from pyproject.toml")


def validate_semver(version: str) -> str:
    if not SEMVER_RE.fullmatch(version):
        raise ValueError(f"version must use MAJOR.MINOR.PATCH semantic format, got {version!r}")
    return version


def main() -> int:
    validate_semver(read_project_version())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
