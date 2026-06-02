"""Runtime plugin hooks for event streams."""

from __future__ import annotations

from events.event import Event
from runtime.event_bus import EventBus


class BasePlugin:
    """Base plugin that can receive runtime events."""

    name = "base_plugin"

    def on_event(self, event: Event) -> None:
        """Handle a runtime event."""


class PluginManager:
    """Registers plugins and forwards event bus events to them."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus
        self._plugins: list[BasePlugin] = []
        self.event_bus.subscribe(self._handle_event)

    def register_plugin(self, plugin: BasePlugin) -> None:
        if plugin not in self._plugins:
            self._plugins.append(plugin)

    def unregister_plugin(self, plugin: BasePlugin) -> None:
        if plugin in self._plugins:
            self._plugins.remove(plugin)

    def plugins(self) -> list[BasePlugin]:
        return list(self._plugins)

    def close(self) -> None:
        self.event_bus.unsubscribe(self._handle_event)

    def _handle_event(self, event: Event) -> None:
        for plugin in list(self._plugins):
            plugin.on_event(event)
