import pytest

from events.event_types import RETRY_COMPLETED, RETRY_STARTED
from runtime.event_bus import EventBus
from runtime.retry_manager import RetryManager


def test_retry_manager_retries_until_success():
    bus = EventBus()
    events = []
    bus.subscribe(events.append)
    manager = RetryManager(bus, max_retries=2, base_delay_seconds=0)
    attempts = {"count": 0}

    def flaky():
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise RuntimeError("temporary")
        return "ok"

    assert manager.run(flaky, agent_id="writer", operation_name="draft") == "ok"
    assert [event.event_type for event in events] == [RETRY_STARTED, RETRY_COMPLETED]
    assert events[0].payload["attempt"] == 1
    assert attempts["count"] == 2


def test_retry_manager_raises_after_exhaustion():
    manager = RetryManager(EventBus(), max_retries=1, base_delay_seconds=0)

    with pytest.raises(RuntimeError):
        manager.run(lambda: (_ for _ in ()).throw(RuntimeError("permanent")))


def test_retry_manager_exponential_delay_calculation():
    manager = RetryManager(EventBus(), base_delay_seconds=0.5, exponential_backoff=True)

    assert manager._delay_for(1) == 0.5
    assert manager._delay_for(3) == 2.0
