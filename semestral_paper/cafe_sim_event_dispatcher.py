from enum import Enum
from event_dispatcher import EventDispatcher
from event_log import EventLog

class Events(Enum):
    NEW_CUSTOMER = "NEW_CUSTOMER"

class CafeSimEventDisp(EventDispatcher):
    def __init__(self):
        super().__init__(enum_class=Events)
        self._log = EventLog()
        self.subscribe(Events.NEW_CUSTOMER, self._on_new_customer)
        pass

    def _on_new_customer(self, name, time, **kwargs):
        self._log.log(time, self._enum_class.NEW_CUSTOMER)
        pass
