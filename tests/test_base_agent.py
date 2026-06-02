from agents.base_agent import BaseAgent
from events.event_types import AGENT_FINISHED, AGENT_STARTED
from runtime.event_bus import EventBus


def test_base_agent_emits_lifecycle_events():
    bus = EventBus()
    events = []
    bus.subscribe(events.append)
    agent = BaseAgent("planner", bus)

    agent.start(task="plan")
    result = agent.run(task="plan")
    agent.finish(result=result)

    assert agent.started is True
    assert agent.finished is True
    assert [event.event_type for event in events] == [AGENT_STARTED, AGENT_FINISHED]
    assert events[0].agent_id == "planner"
    assert events[0].payload == {"context": {"task": "plan"}}
    assert events[1].payload == {"result": {"task": "plan"}}
