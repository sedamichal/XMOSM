from enum import Enum
from sim_status import SimulationStatus


class Stats(Enum):    
    WAIT_CASHIER     = 'wait_cashier'
    WAIT_DRINK       = 'wait_drink'
    TIME_IN_SYSTEM   = 'time_in_system'
    TOTAL_CUSTOMERS  = 'total_customers'
    SERVED_CUSTOMERS = 'served_customers'
    CASHIER_QUEUE    = 'cashier_queue'
    DRINK_QUEUE      = 'drink_queue'
    QUEUE_TIMES      = 'queue_times'


class CafeSimulationStatus(SimulationStatus):
    def __init__(self):
        super().__init__(enum_stats=Stats)
