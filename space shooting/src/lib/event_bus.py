class EventBus:
    def __init__(self):
        self._listeners = {}

    def on(self, event_name, callback):
        """Register a callback for an event."""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def off(self, event_name, callback):
        """Unregister a callback for an event."""
        if event_name in self._listeners:
            try:
                self._listeners[event_name].remove(callback)
            except ValueError:
                pass

    def emit(self, event_name, *args, **kwargs):
        """Trigger all callbacks registered for the event."""
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                callback(*args, **kwargs)
