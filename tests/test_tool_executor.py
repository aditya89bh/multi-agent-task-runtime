import pytest

from events.event_types import TOOL_CALLED, TOOL_RETURNED
from runtime.event_bus import EventBus
from tools.tool_executor import ToolExecutor


def test_tool_executor_emits_tool_call_and_return_events():
    bus = EventBus()
    events = []
    bus.subscribe(events.append)
    executor = ToolExecutor(bus)
    executor.register_tool("add", lambda left, right: left + right)

    result = executor.execute("add", 2, 3, agent_id="planner")

    assert result == 5
    assert [event.event_type for event in events] == [TOOL_CALLED, TOOL_RETURNED]
    assert events[0].payload == {"tool_name": "add", "args": [2, 3], "kwargs": {}}
    assert events[1].payload["tool_name"] == "add"
    assert events[1].payload["result"] == 5
    assert events[1].payload["duration_ms"] >= 0


def test_tool_executor_rejects_unknown_tools():
    executor = ToolExecutor(EventBus())

    with pytest.raises(KeyError):
        executor.execute("missing")
