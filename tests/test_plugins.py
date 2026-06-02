from events.event import Event
from events.event_types import AGENT_STARTED
from runtime.event_bus import EventBus
from runtime.plugins import BasePlugin, PluginManager


class RecordingPlugin(BasePlugin):
    name = "recording"

    def __init__(self):
        self.events = []

    def on_event(self, event):
        self.events.append(event)


def test_plugin_manager_forwards_events_to_registered_plugins():
    bus = EventBus()
    manager = PluginManager(bus)
    plugin = RecordingPlugin()
    manager.register_plugin(plugin)
    event = Event(event_type=AGENT_STARTED)

    bus.publish(event)

    assert plugin.events == [event]
    manager.unregister_plugin(plugin)
    bus.publish(event)
    assert plugin.events == [event]
    manager.close()
