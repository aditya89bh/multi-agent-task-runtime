import json

from benchmarks.load_test import run_load_test, write_results


def test_load_test_small_run_generates_metrics(tmp_path):
    result = run_load_test(event_count=60, agent_count=3)

    assert result["event_count"] == 60
    assert result["replayed_events"] == 60
    assert result["write_throughput_events_per_second"] > 0
    output = tmp_path / "load_results.json"
    write_results(result, output)
    assert json.loads(output.read_text(encoding="utf-8"))["event_count"] == 60
