from enum import Enum
import yaml
from sim_status import SimulationStatus
from cafe_sim_config import CafeSimulationConfig


class StatsUS(Enum):
    WAIT_CASHIER = "wait_cashier"
    WAIT_DRINK = "wait_drink"
    TIME_IN_SYSTEM = "time_in_system"
    TOTAL_CUSTOMERS = "total_customers"
    SERVED_CUSTOMERS = "served_customers"
    CASHIER_QUEUE = "cashier_queue"
    DRINK_QUEUE = "drink_queue"
    QUEUE_TIMES = "queue_times"


class CafeSimulationStatusEU(SimulationStatus):
    def __init__(self):
        super().__init__(enum_stats=StatsUS)


class CafeSimulationConfigEU(CafeSimulationConfig):

    def _default_yaml_name(self):
        return "eu_default_config.yaml"

    def save_ui(self):
        main_section = self._config.get("main")
        drink_wait_section = self._config.get("drink_wait")

        for key, widget in self._ui_elements.items():
            if main_section != None and key in main_section:
                main_section[key]["default"] = widget.value
            elif drink_wait_section != None and key in drink_wait_section:
                drink_wait_section[key]["default"] = widget.value

        try:
            with open(self._yaml_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    self._config,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                )
            print(f"Konfigurace byla úspěšně uložena do: {self._yaml_file}")
        except Exception as e:
            print(f"Chyba při ukládání: {e}")
            pass
