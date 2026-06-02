"""Compressed JSONL event archive helpers."""

from __future__ import annotations

import gzip
import json
from collections.abc import Iterable
from pathlib import Path

from events.event import Event
from runtime.paths import ensure_input_file, ensure_output_file

PathLike = str | Path


def compress_jsonl(source_path: PathLike, archive_path: PathLike | None = None) -> Path:
    source = ensure_input_file(source_path, "source")
    target = ensure_output_file(Path(archive_path) if archive_path is not None else source.with_suffix(source.suffix + ".gz"), "archive")
    if source.resolve() == target.resolve():
        raise ValueError("archive path must differ from source path")
    with source.open("rb") as src, gzip.open(target, "wb") as dst:
        dst.writelines(src)
    return target


def write_jsonl_gz(events: Iterable[Event], archive_path: PathLike) -> Path:
    target = ensure_output_file(archive_path, "archive")
    with gzip.open(target, "wt", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event.to_dict(), sort_keys=True) + "\n")
    return target


def read_jsonl_gz(archive_path: PathLike) -> list[Event]:
    source = ensure_input_file(archive_path, "archive")
    with gzip.open(source, "rt", encoding="utf-8") as file:
        return [Event(**json.loads(line)) for line in file if line.strip()]
