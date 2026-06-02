import json

from benchmarks.runtime_benchmark import run_benchmark, write_results


def test_runtime_benchmark_generates_large_event_summary(tmp_path):
    result = run_benchmark(agent_count=2, events_per_agent=3)

    assert result["agent_count"] == 2
    assert result["total_events"] == 28
    assert result["summary"]["tool_calls"] == 6
    assert result["summary"]["memory_reads"] == 6
    assert result["summary"]["memory_writes"] == 6

    output = tmp_path / "latest_results.json"
    write_results(result, output)
    assert json.loads(output.read_text(encoding="utf-8"))["total_events"] == 28
