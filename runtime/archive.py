"""Compressed JSONL event archive helpers."""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Iterable, List, Union

from events.event import Event

PathLike = Union[str, Path]


def compress_jsonl(source_path: PathLike, archive_path: PathLike | None = None) -> Path:
    source = Path(source_path)
    target = Path(archive_path) if archive_path is not None else source.with_suffix(source.suffix + ".gz")
    target.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as src, gzip.open(target, "wb") as dst:
        dst.writelines(src)
    return target


def write_jsonl_gz(events: Iterable[Event], archive_path: PathLike) -> Path:
    target = Path(archive_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(target, "wt", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event.to_dict(), sort_keys=True) + "\n")
    return target


def read_jsonl_gz(archive_path: PathLike) -> List[Event]:
    with gzip.open(archive_path, "rt", encoding="utf-8") as file:
        return [Event(**json.loads(line)) for line in file if line.strip()]
