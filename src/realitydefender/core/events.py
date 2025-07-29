"""
Event handling for asynchronous operations
"""

from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, overload

from realitydefender.model import ErrorHandler, EventName, ResultHandler

# Create a generic type for event names that can be either the specific EventName type
# or any string (for testing purposes)
E = TypeVar("E", EventName, str)
CallbackT = TypeVar("CallbackT", bound=Callable[..., Any])


class EventEmitter:
    """
    Simple event emitter for handling callbacks and events
    """

    def __init__(self) -> None:
        """Initialize the event emitter with empty event handlers"""
        self._events: Dict[str, List[Callable]] = {}

    @overload
    def on(
        self, event: EventName, callback: Union[ResultHandler, ErrorHandler]
    ) -> None: ...

    @overload
    def on(self, event: str, callback: Callable[..., Any]) -> None: ...

    def on(self, event: str, callback: Callable[..., Any]) -> None:
        """
        Register an event handler

        Args:
            event: Event name to listen for
            callback: Function to call when event occurs
        """
        if event not in self._events:
            self._events[event] = []
        self._events[event].append(callback)

    @overload
    def once(
        self, event: EventName, callback: Union[ResultHandler, ErrorHandler]
    ) -> None: ...

    @overload
    def once(self, event: str, callback: Callable[..., Any]) -> None: ...

    def once(self, event: str, callback: Callable[..., Any]) -> None:
        """
        Register an event handler that will be removed after being called once

        Args:
            event: Event name to listen for
            callback: Function to call when event occurs
        """

        def one_time_handler(*args: Any, **kwargs: Any) -> Any:
            self.remove_listener(event, one_time_handler)
            return callback(*args, **kwargs)

        self.on(event, one_time_handler)

    @overload
    def emit(self, event: EventName, *args: Any, **kwargs: Any) -> bool: ...

    @overload
    def emit(self, event: str, *args: Any, **kwargs: Any) -> bool: ...

    def emit(self, event: str, *args: Any, **kwargs: Any) -> bool:
        """
        Emit an event with arguments

        Args:
            event: Event name to emit
            *args: Arguments to pass to event handlers
            **kwargs: Keyword arguments to pass to event handlers

        Returns:
            True if the event had listeners, False otherwise
        """
        if event not in self._events:
            return False

        for callback in self._events[event]:
            callback(*args, **kwargs)

        return len(self._events[event]) > 0

    @overload
    def remove_listener(
        self, event: EventName, callback: Callable[..., Any]
    ) -> None: ...

    @overload
    def remove_listener(self, event: str, callback: Callable[..., Any]) -> None: ...

    def remove_listener(self, event: str, callback: Callable[..., Any]) -> None:
        """
        Remove a specific event listener

        Args:
            event: Event name
            callback: Function to remove
        """
        if event not in self._events:
            return

        self._events[event] = [cb for cb in self._events[event] if cb != callback]

    @overload
    def remove_all_listeners(self, event: Optional[EventName] = None) -> None: ...

    @overload
    def remove_all_listeners(self, event: Optional[str] = None) -> None: ...

    def remove_all_listeners(self, event: Optional[str] = None) -> None:
        """
        Remove all listeners for an event or all events

        Args:
            event: Event name, or None to remove all events
        """
        if event is not None:
            self._events[event] = []
        else:
            self._events = {}
