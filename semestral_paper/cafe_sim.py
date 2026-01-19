import simpy
import random
import os
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
import yaml
import matplotlib.pyplot as plt
from IPython.display import display, clear_output
import ipywidgets as ipw
from ipywidgets import interact, interactive, fixed, interact_manual

from cafe_sim_config import *
from cafe_sim_status import *
from event_dispatcher import EventDispatcher

class CafeSimulationProcess(ABC):
    def __init__(self, env: simpy.Environment):
        self._env = env


class CafeSimulationCustomer(CafeSimulationProcess):
    def __init__(self, env: simpy.Environment):
        super().__init__(env=env)
        self._arrival_time = env.now


class CafeSimulation(ABC):

    def __init__(self, config: CafeSimulationConfig, stats: CafeSimulationStatus, event_dispatcher: EventDispatcher):
        self._config = config
        self._status = stats
        self._event_dispatcher = event_dispatcher

    def _get_resources(self):
        pass

    def customer(self, env, name, cashier, baristas, tables):
        """Proces zákazníka."""

        arrival_time = env.now
        self._status["total_customers"] += 1

        # Fronta u pokladny
        cashier_queue_start = env.now
        with cashier.request() as req:
            yield req
            cashier_wait = env.now - cashier_queue_start
            self._stats["wait_cashier"].append(cashier_wait)

            service_time = max(
                0.5,
                random.gauss(
                    self._config["cashier_time_mean"], self._config["cashier_time_std"]
                ),
            )
            yield env.timeout(service_time)

        # Vyber napoje
        drink_type = random.choice(self._config.drinks)

        # Fronta u vydeje
        drink_queue_start = env.now
        with baristas.request() as req:
            yield req

            drink_wait = env.now - drink_queue_start
            self._stats["wait_drink"].append(drink_wait)

            prep_time = self._config[drink_type]
            yield env.timeout(prep_time)

        # Sednout/odnest
        wants_table = random.random() < self._config["p_wants_table"]

        if wants_table and len(tables.users) < tables.capacity:
            table_req = tables.request()
            yield table_req

            consumption_time = max(
                5,
                random.gauss(
                    self._config["consumption_time_mean"],
                    self._config["consumption_time_std"],
                ),
            )
            yield env.timeout(consumption_time)
            tables.release(table_req)

        # Celkovy cas
        total_time = env.now - arrival_time
        self._stats["time_in_system"].append(total_time)
        self._stats["served_customers"] += 1

    def _reset_stats(self):
        self._stats["customer_count"] = 0
        self._stats["served_customers"] = 0
        self._stats["time_in_system"] = {}
        self._stats["wait_cashier"] = {}

    def customer_generator(self, env, cashier, baristas, tables):
        """Generuje příchody zákazníků."""

        self._stats["customer_count"] = 0
        self._stats["served_customers"] = 0

        while True:
            # exponencialni distribuce
            inter_arrival = random.expovariate(self._config["arrival_rate"] / 60)
            yield env.timeout(inter_arrival)

            self._stats["customer_count"] += 1
            env.process(
                self.customer(
                    env,
                    f"Customer_{self._stats["customer_count"]}",
                    cashier,
                    baristas,
                    tables,
                )
            )

    def queue_monitor(self, env, cashier, baristas):
        """Zaznamenává délky front."""
        while True:
            self._stats["queue_times"].append(env.now)
            self._stats["cashier_queue"].append(len(cashier.queue))
            self._stats["drink_queue"].append(len(baristas.queue))
            yield env.timeout(5)

    @abstractmethod
    def _prepare_process(self):
        pass

    def run(self):
        """Spustí simulaci."""
        env = simpy.Environment()

        self._prepare_process(env)

        env.run(until=self.params["sim_time"])

        return self.stats


class CafeSimulatorUS(CafeSimulation):

    def _get_config(self, config_file):
        return CafeSimulationConfigEU(yaml_file=config_file)

    def _get_stats(self):
        return {
            "wait_cashier": [],
            "wait_drink": [],
            "time_in_system": [],
            "total_customers": 0,
            "served_customers": 0,
            "cashier_queue": [],
            "drink_queue": [],
            "queue_times": [],
        }

    def _prepare_process(self, env):
        cashier = simpy.Resource(env, capacity=self._config["num_cashiers"])
        baristas = simpy.Resource(env, capacity=self._config["num_baristas"])
        tables = simpy.Resource(env, capacity=self._config["num_tables"])

        env.process(self.customer_generator(env, cashier, baristas, tables))
        env.process(self.queue_monitor(env, cashier, baristas))
