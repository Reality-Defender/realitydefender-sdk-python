"""
Tests for the event emitter module
"""

from realitydefender.core.events import EventEmitter


def test_on_and_emit() -> None:
    """Test registering event handlers and emitting events"""
    emitter = EventEmitter()

    # Track calls to event handlers
    calls = []

    # Register handlers
    emitter.on("event1", lambda: calls.append("event1"))
    emitter.on("event2", lambda x: calls.append(f"event2: {x}"))
    emitter.on("event2", lambda x: calls.append(f"event2 second: {x}"))

    # Emit events
    emitter.emit("event1")
    assert calls == ["event1"]

    emitter.emit("event2", "test")
    assert calls == ["event1", "event2: test", "event2 second: test"]

    # Emit event with no handlers
    result = emitter.emit("non_existent")
    assert result is False
    assert calls == ["event1", "event2: test", "event2 second: test"]


def test_once() -> None:
    """Test one-time event handlers"""
    emitter = EventEmitter()

    # Track calls to event handler
    calls = []

    # Register handler that should be called only once
    emitter.once("test", lambda: calls.append("called"))

    # Emit event twice
    emitter.emit("test")
    emitter.emit("test")

    # Handler should only be called once
    assert calls == ["called"]


def test_remove_listener() -> None:
    """Test removing specific event listeners"""
    emitter = EventEmitter()

    # Track calls to event handlers
    calls = []

    # Define handlers
    def handler1() -> None:
        calls.append("handler1")

    def handler2() -> None:
        calls.append("handler2")

    # Register handlers
    emitter.on("test", handler1)
    emitter.on("test", handler2)

    # Remove first handler
    emitter.remove_listener("test", handler1)

    # Emit event
    emitter.emit("test")

    # Only second handler should be called
    assert calls == ["handler2"]

    # Remove non-existent handler (should not error)
    emitter.remove_listener("test", lambda: None)
    emitter.remove_listener("non_existent", handler1)


def test_remove_all_listeners() -> None:
    """Test removing all event listeners"""
    emitter = EventEmitter()

    # Track calls to event handlers
    calls = []

    # Register handlers for multiple events
    emitter.on("event1", lambda: calls.append("event1"))
    emitter.on("event2", lambda: calls.append("event2"))

    # Remove all listeners for event1
    emitter.remove_all_listeners("event1")

    # Emit events
    emitter.emit("event1")
    emitter.emit("event2")

    # Only event2 handler should be called
    assert calls == ["event2"]

    # Remove all listeners for all events
    emitter.remove_all_listeners()

    # Emit events again
    emitter.emit("event1")
    emitter.emit("event2")

    # No additional calls should be made
    assert calls == ["event2"]
