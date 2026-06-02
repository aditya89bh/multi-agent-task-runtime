import json

from benchmarks.stress_benchmark import run_stress, write_results


def test_stress_benchmark_small_run_generates_results(tmp_path):
    result = run_stress(event_count=60, agent_count=3)
    assert result["event_count"] == 60
    assert result["summary"]["total_events"] == 60
    output = tmp_path / "stress_results.json"
    write_results(result, output)
    assert json.loads(output.read_text(encoding="utf-8"))["event_count"] == 60
