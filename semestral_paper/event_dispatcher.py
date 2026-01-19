from abc import ABC, abstractmethod
from enum import Enum


class EventDispatcher(ABC):
    _listeners = {}

    def __init__(self, enum_class: type[Enum]):
        self._enum_class = enum_class
        self.clear_listeners()

    def events(self):
        return self._enum_class

    def subscribe(self, event_type, callback):
        """Ruční registrace (vhodné pro metody tříd s 'self')"""

        if not isinstance(event_type, self._enum_class):
            raise TypeError(
                f"Očekáván {self._enum_class}, dostal jsem {type(event_type)}"
            )

        self._listeners[event_type].append(callback)

    def emit(self, event_type: Enum, **kwargs):
        """Vystřelí událost a předá data."""

        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                callback(**kwargs)

    def clear_listeners(self):
        """Odstraní všechny odebíratele (užitečné mezi testy)."""

        self._listeners = {event: [] for event in self._enum_class}
