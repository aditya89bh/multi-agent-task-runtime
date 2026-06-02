"""Structured runtime configuration."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RuntimeConfig:
    """Runtime paths and tuning knobs with safe defaults."""

    log_path: Path = Path("logs/runtime_events.jsonl")
    sqlite_db_path: Path = Path("runtime_events.db")
    dashboard_refresh_interval: float = 1.0
    benchmark_output_path: Path = Path("benchmarks/results/latest_results.json")

    @classmethod
    def load(cls, config_path: str | Path | None = None, environ: dict[str, str] | None = None) -> RuntimeConfig:
        env = os.environ if environ is None else environ
        values: dict[str, Any] = {}
        if config_path is not None:
            path = Path(config_path)
            if path.exists():
                loaded = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(loaded, dict):
                    raise ValueError("runtime config file must contain a JSON object")
                values.update(loaded)
        mapping = {
            "RUNTIME_LOG_PATH": "log_path",
            "RUNTIME_SQLITE_DB_PATH": "sqlite_db_path",
            "RUNTIME_DASHBOARD_REFRESH_INTERVAL": "dashboard_refresh_interval",
            "RUNTIME_BENCHMARK_OUTPUT_PATH": "benchmark_output_path",
        }
        for env_name, field_name in mapping.items():
            if env_name in env:
                values[field_name] = env[env_name]
        return cls(
            log_path=Path(values.get("log_path", cls.log_path)),
            sqlite_db_path=Path(values.get("sqlite_db_path", cls.sqlite_db_path)),
            dashboard_refresh_interval=float(values.get("dashboard_refresh_interval", cls.dashboard_refresh_interval)),
            benchmark_output_path=Path(values.get("benchmark_output_path", cls.benchmark_output_path)),
        )
