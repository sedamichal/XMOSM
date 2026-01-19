from enum import Enum
import yaml
import simpy
import random
from IPython.display import display, clear_output
import ipywidgets as ipw

from sim_status import SimulationStatus
from cafe_sim_config import CafeSimulationConfig
from event_dispatcher import EventDispatcher


class StatsUS(Enum):
    WAIT_CASHIER = "wait_cashier"
    WAIT_DRINK = "wait_drink"
    TIME_IN_SYSTEM = "time_in_system"
    TOTAL_CUSTOMERS = "total_customers"
    SERVED_CUSTOMERS = "served_customers"
    CASHIER_QUEUE = "cashier_queue"
    DRINK_QUEUE = "drink_queue"
    QUEUE_TIMES = "queue_times"


class CafeSimulationStatusUS(SimulationStatus):
    def __init__(self):
        super().__init__(enum_stats=StatsUS)


class CafeSimulationEventUS(Enum):
    NEW_CUSTOMER = "new_customer"
    CASHIER_WAIT_START = "cashier_wait_start"
    CASHIER_WAIT_END = "cashier_wait_end"
    CUSTOMER_RENEGED = "customer_reneged"
    SERVICE_START = "service_start"
    SERVICE_END = "service_end"
    DRINK_QUEUE_START = "drink_queue_start"
    DRINK_PREPARATION_START = "drink_preparation_start"
    DRINK_PREPARATION_END = "drink_preparation_end"
    DRINK_QUEUE_END = "drink_queue_end"
    DRINK_SELECTED = "drink_selected"
    WANTS_TABLE = "wants_table"
    CONSUMPTION_START = "consumption_start"
    CONSUMPTION_END = "consumption_end"
    CUSTOMER_LEFT = "customer_left"
    QUEUE_MONITOR = "queue_monitor"


class CafeSimulationEventDespatcherUS(EventDispatcher):
    def __init__(self):
        super().__init__(enum_class=CafeSimulationEventUS)

        self.subscribe(CafeSimulationEventUS.NEW_CUSTOMER, self._on_new_customer)
        self.subscribe(
            CafeSimulationEventUS.CASHIER_WAIT_START, self._on_cashier_wait_start
        )
        self.subscribe(
            CafeSimulationEventUS.CASHIER_WAIT_END, self._on_cashier_wait_end
        )
        self.subscribe(
            CafeSimulationEventUS.CUSTOMER_RENEGED, self._on_customer_reneged
        )
        self.subscribe(CafeSimulationEventUS.SERVICE_START, self._on_service_start)
        self.subscribe(CafeSimulationEventUS.SERVICE_END, self._on_service_end)
        self.subscribe(
            CafeSimulationEventUS.DRINK_QUEUE_START, self._on_drink_queue_start
        )
        self.subscribe(CafeSimulationEventUS.DRINK_PREPARATION_START, self._on_drink_preparation_start)
        self.subscribe(
            CafeSimulationEventUS.DRINK_PREPARATION_END, self._on_drink_preparation_end
        )
        self.subscribe(CafeSimulationEventUS.DRINK_SELECTED, self._on_drink_selected)
        self.subscribe(CafeSimulationEventUS.WANTS_TABLE, self._on_wants_table)
        self.subscribe(
            CafeSimulationEventUS.CONSUMPTION_START, self._on_consumption_start
        )
        self.subscribe(CafeSimulationEventUS.CONSUMPTION_END, self._on_consumption_end)
        self.subscribe(CafeSimulationEventUS.CUSTOMER_LEFT, self._on_customer_left)
        self.subscribe(CafeSimulationEventUS.QUEUE_MONITOR, self._on_queue_monitor)

    def _on_new_customer(self, time, customer_id):
        pass

    def _on_cashier_wait_start(self, time, customer_id):
        pass

    def _on_cashier_wait_end(self, time, customer_id):
        pass

    def _on_customer_reneged(self, time, customer_id):
        pass

    def _on_service_start(self, time, customer_id):
        pass

    def _on_service_end(self, time, customer_id):
        pass

    def _on_drink_queue_start(self, time, customer_id):
        pass

    def _on_drink_preparation_start(self, time, customer_id):
        pass

    def _on_drink_preparation_end(self, time, customer_id):
        pass

    def _on_drink_selected(self, time, customer_id, drink_type):
        pass

    def _on_wants_table(self, time, customer_id, tables_capacity):
        pass

    def _on_consumption_start(self, time, customer_id):
        pass

    def _on_consumption_end(self, time, customer_id):
        pass

    def _on_customer_left(self, time, customer_id):
        pass

    def _on_queue_monitor(self, time, cashiers:simpy.Resource, baristas:simpy.Resource, table_places:simpy.Resource):
        pass


class CafeSimulationConfigUS(CafeSimulationConfig):

    def _default_yaml_name(self):
        return "us_default_config.yaml"

    def save_ui(self):
        # main_section = self._config.get("main")
        # drink_wait_section = self._config.get("drink_wait")

        # for key, widget in self._ui_elements.items():
            
        #     if main_section != None and key in main_section:
        #         main_section[key]["default"] = widget.value
        #     elif drink_wait_section != None and key in drink_wait_section:
        #         drink_wait_section[key]["default"] = widget.value

        for key, widget in self._ui_elements.items():
            self._update_recursive(self._config, key, widget.value)

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
    
    def _update_recursive(self, data, key_to_find, new_value):
        if isinstance(data, dict):
            for k, v in data.items():
                if k == key_to_find and isinstance(v, dict) and "default" in v:
                    v["default"] = new_value
                else:
                    self._update_recursive(v, key_to_find, new_value)


class CafeSimulationUS:
    _cashier = None
    _baristas = None
    _tables = None
    _env = None
    _customers_cnt=0

    def __init__(self):
        self._config = CafeSimulationConfigUS()
        # self._status = CafeSimulationStatusUS()
        self._event_dispatcher = CafeSimulationEventDespatcherUS()

    def create_ui(self):
        self._config.create_ui()
        self._create_run_button()

    def run(self):
        """Spustí simulaci."""
        self._prepare_process()
        self._env.run(until=self._get_sim_time())

    def _prepare_process(self):
        self._customers_cnt = 0

        self._env = simpy.Environment()
        self._cashiers = simpy.Resource(self._env, capacity=self._get_cashiers_num())
        self._baristas = simpy.Resource(self._env, capacity=self._get_baristas_num())
        self._table_places = simpy.Resource(
            self._env, capacity=self._get_table_places_num()
        )

        self._env.process(self._customer_generator())
        self._env.process(self._queue_monitor())

    def _queue_monitor(self):
        """Zaznamenávání délky front."""
        while True:
            self._event_dispatcher.emit(
                CafeSimulationEventUS.QUEUE_MONITOR,
                time=self._env.now,
                cashiers=self._cashiers,
                baristas=self._baristas,
                table_places=self._table_places,
            )
            yield self._env.timeout(self._get_simulation_step())

    def _customer_generator(self):
        while True:
            inter_arrival = self._get_arrival_interval()
            self._customers_cnt += 1
            yield self._env.timeout(inter_arrival)
            self._env.process(self._customer(self._customers_cnt))

    def _customer(self, id):
        """Proces zákazníka."""

        self._event_dispatcher.emit(
            CafeSimulationEventUS.NEW_CUSTOMER, time=self._env.now, customer_id=id
        )

        # Fronta u pokladny
        self._event_dispatcher.emit(
            CafeSimulationEventUS.CASHIER_WAIT_START, time=self._env.now, customer_id=id
        )
        with self._cashiers.request() as req:
            # Čekáme buď na uvolnění pokladny, nebo na vypršení trpělivosti
            patience = self._get_patience()
            result = yield req | self._env.timeout(patience)
            if req not in result:
                # Zákazník to vzdal (vypršel timeout trpělivosti)
                self._event_dispatcher.emit(
                    CafeSimulationEventUS.CUSTOMER_RENEGED,
                    time=self._env.now,
                    customer_id=id,
                )
                # Proces zákazníka končí - odchází z kavárny
                return

            # Zákazník se dočkal (pokladna je volná)
            self._event_dispatcher.emit(
                CafeSimulationEventUS.CASHIER_WAIT_END,
                time=self._env.now,
                customer_id=id,
            )

            # Samotná obsluha
            self._event_dispatcher.emit(
                CafeSimulationEventUS.SERVICE_START, time=self._env.now, customer_id=id
            )
            service_time = self._get_service_time()
            yield self._env.timeout(service_time)
            self._event_dispatcher.emit(
                CafeSimulationEventUS.SERVICE_END, time=self._env.now, customer_id=id
            )

        # Vyber napoje
        drink_type = random.choice(self._config.drinks)
        self._event_dispatcher.emit(
            CafeSimulationEventUS.DRINK_SELECTED, time=self._env.now, customer_id=id
        )

        self._event_dispatcher.emit(
            CafeSimulationEventUS.DRINK_QUEUE_START, time=self._env.now, customer_id=id
        )
        # Fronta u vydeje
        with self._baristas.request() as req:
            yield req
            self._event_dispatcher.emit(
                CafeSimulationEventUS.DRINK_PREPARATION_START,
                time=self._env.now,
                customer_id=id,
            )

            prep_time = self._get_drink_prep_time(drink_type)
            yield self._env.timeout(prep_time)
            self._event_dispatcher.emit(
                CafeSimulationEventUS.DRINK_PREPARATION_END,
                time=self._env.now,
                customer_id=id,
            )

        # Sednout/odnest
        wants_table = self._wants_table()
        if wants_table:
            self._event_dispatcher.emit(
                CafeSimulationEventUS.WANTS_TABLE,
                time=self._env.now,
                customer_id=id,
                tables_capacity=self._table_places.capacity,
            )

        if wants_table and len(self._table_places.users) < self._table_places.capacity:
            with self._table_places.request() as table_req:
                yield table_req
                self._event_dispatcher.emit(
                    CafeSimulationEventUS.CONSUMPTION_START,
                    time=self._env.now,
                    customer_id=id,
                )

                consumption_time = self._get_consumption_time()
                yield self._env.timeout(consumption_time)
                self._event_dispatcher.emit(
                    CafeSimulationEventUS.CONSUMPTION_END,
                    time=self._env.now,
                    customer_id=id,
                )

        self._event_dispatcher.emit(
            CafeSimulationEventUS.CUSTOMER_LEFT, time=self._env.now, customer_id=id
        )

    def _create_run_button(self):
        run_btn = ipw.Button(
            description="Spustit",
            button_style="success",  # Zelené tlačítko
            icon="save",
        )

        def on_click(b):
            self.run()

        run_btn.on_click(on_click)
        display(run_btn)

    def _get_sim_time(self):
        return self._config["simulation_time"]

    def _get_patience(self):
        patience = max(
            0.5,
            random.gauss(
                self._config["queue_patience_mean"],
                self._config["queue_patience_std"],
            ),
        )
        return patience

    def _get_service_time(self):
        service_time = max(
            0.5,
            random.gauss(
                self._config["cashier_time_mean"], self._config["cashier_time_std"]
            ),
        )
        return service_time

    def _get_drink(self):
        return random.choice(self._config.drinks)

    def _get_drink_prep_time(self, drink_type):
        return self._config[drink_type]

    def _wants_table(self):
        return random.random() < self._config["p_wants_table"]

    def _get_cashiers_num(self):
        return self._config["num_cashiers"]

    def _get_baristas_num(self):
        return self._config["num_baristas"]

    def _get_table_places_num(self):
        return self._config["num_table_places"]

    def _get_simulation_step(self):
        return self._config["simulation_step"]

    def _get_consumption_time(self):
        consumption_time = max(
            5,
            random.gauss(
                self._config["consumption_time_mean"],
                self._config["consumption_time_std"],
            ),
        )
        return consumption_time

    def _get_arrival_interval(self):
        arrival_rate = self._config["arrival_rate"]
        # exponencialni distribuce
        return random.expovariate(arrival_rate / 60)
