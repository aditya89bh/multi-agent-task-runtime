from events.event import Event
from events.event_types import AGENT_STARTED
from runtime.event_bus import EventBus


def test_event_bus_publishes_to_multiple_subscribers():
    bus = EventBus()
    first = []
    second = []
    bus.subscribe(first.append)
    bus.subscribe(second.append)

    event = Event(event_type=AGENT_STARTED, agent_id="planner")
    bus.publish(event)

    assert first == [event]
    assert second == [event]


def test_event_bus_unsubscribes_subscriber():
    bus = EventBus()
    received = []
    bus.subscribe(received.append)
    bus.unsubscribe(received.append)

    bus.publish(Event(event_type=AGENT_STARTED, agent_id="planner"))

    assert received == []
