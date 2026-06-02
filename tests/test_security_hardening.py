import pytest

from events.event import Event
from events.event_types import AGENT_STARTED, FAILURE_OCCURRED
from reports.html_report import HTMLReportGenerator
from runtime.archive import compress_jsonl, read_jsonl_gz, write_jsonl_gz
from runtime.paths import ensure_input_file, ensure_output_file


def test_path_helpers_reject_directories_for_file_inputs_and_outputs(tmp_path):
    with pytest.raises(ValueError):
        ensure_input_file(tmp_path, "input")
    with pytest.raises(ValueError):
        ensure_output_file(tmp_path, "output")


def test_archive_helpers_reject_unsafe_paths(tmp_path):
    source = tmp_path / "events.jsonl"
    source.write_text('{"bad": "missing fields"}\n', encoding="utf-8")

    with pytest.raises(ValueError):
        compress_jsonl(source, source)
    with pytest.raises(ValueError):
        write_jsonl_gz([Event(event_type=AGENT_STARTED)], tmp_path)
    with pytest.raises(ValueError):
        read_jsonl_gz(tmp_path)


def test_html_report_rejects_directory_output_and_escapes_payload(tmp_path):
    with pytest.raises(ValueError):
        HTMLReportGenerator().generate([Event(event_type=AGENT_STARTED)], tmp_path)

    report = HTMLReportGenerator().generate([Event(event_type=FAILURE_OCCURRED, payload={"value": "<script>"})], tmp_path / "report.html")
    assert "&lt;script&gt;" in report.read_text(encoding="utf-8")
