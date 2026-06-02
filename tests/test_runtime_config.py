import json
from pathlib import Path

from runtime.config import RuntimeConfig


def test_runtime_config_uses_sensible_defaults():
    config = RuntimeConfig.load(environ={})

    assert config.log_path == Path("logs/runtime_events.jsonl")
    assert config.sqlite_db_path == Path("runtime_events.db")
    assert config.dashboard_refresh_interval == 1.0
    assert config.benchmark_output_path == Path("benchmarks/results/latest_results.json")


def test_runtime_config_loads_json_file_and_environment_overrides(tmp_path):
    path = tmp_path / "runtime.json"
    path.write_text(json.dumps({"log_path": "custom/events.jsonl", "dashboard_refresh_interval": 2}), encoding="utf-8")

    config = RuntimeConfig.load(path, environ={"RUNTIME_SQLITE_DB_PATH": "custom/events.db"})

    assert config.log_path == Path("custom/events.jsonl")
    assert config.sqlite_db_path == Path("custom/events.db")
    assert config.dashboard_refresh_interval == 2.0
