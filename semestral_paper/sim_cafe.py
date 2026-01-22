import pandas as pd
import numpy as np
import simpy
import random
import math
import ipywidgets as ipw
from IPython.display import display, clear_output
from enum import Enum
from dataclasses import dataclass, field
import time
from tqdm.notebook import tqdm
from bqplot import LinearScale, Axis, Lines, Figure, Label, Bars
from collections import defaultdict

# Import tvých modulů
from sim_configuration import ConfigurationManager, ConfigNode, seconds_to_hms

# =================================================================
# 1. POMOCNÉ TŘÍDY A LOGIKY
# =================================================================


class StatusLog:

    def __init__(self, min_time=0, max_time=1440, total_table_capacity=0):
        self._log = []
        self._min_time = float(min_time)
        self._max_time = float(max_time)
        self._total_table_capacity = total_table_capacity
        self._figs = []
        # Definice linek pro tři grafy
        self._queue_lines = None
        self._capacity_lines = None
        self._summary_lines = None

    def show(self):
        # Fixní X škála pro všechny grafy stejná
        x_sc = LinearScale(min=self._min_time, max=self._max_time)
        y_sc_q = LinearScale(min=0.0)
        y_sc_c = LinearScale(
            min=0.0,
        )
        y_sc_s = LinearScale(min=0.0)

        # 1. Graf: Fronty + Obsazená sedadla + kapacita stolu
        self._queue_lines = Lines(
            x=[],
            y=[],
            scales={"x": x_sc, "y": y_sc_q},
            colors=["#E74C3C", "#F1C40F", "#2ECC71", "#95A5A6"],
            labels=[
                "Fronta u pokladny",
                "Čekající na nápoj",
                "Obsazená sedadla",
                "Kapacita stolů",
            ],
            display_legend=True,
            # stroke_width=[2, 2, 2, 1.5],  # 4. čára trochu tenčí
            opacities=[1.0, 1.0, 1.0, 0.6],  # 4. čára průhlednější
        )

        # 2. Graf: Kapacity
        self._capacity_lines = Lines(
            x=[],
            y=[],
            scales={"x": x_sc, "y": y_sc_c},
            colors=["#3498DB", "#9B59B6"],
            labels=["Kapacita Pokladní", "Kapacita Baristi"],
            display_legend=True,
        )

        # 3. Graf: Statistiky
        self._summary_lines = Lines(
            x=[],
            y=[],
            scales={"x": x_sc, "y": y_sc_s},
            colors=["#27AE60", "#E67E22"],
            labels=["Obslouženo", "Odešlo (reneged)"],
            display_legend=True,
        )

        # Sestavení figur s fixní výškou pro dobrou scannabilitu
        fig_q = Figure(
            marks=[self._queue_lines],
            axes=[
                Axis(scale=x_sc, label="Čas (min)"),
                Axis(scale=y_sc_q, orientation="vertical"),
            ],
            title="Stav front a sedadel",
            layout={"height": "250px", "width": "98%"},
        )

        fig_c = Figure(
            marks=[self._capacity_lines],
            axes=[
                Axis(scale=x_sc, label="Čas (min)"),
                Axis(
                    scale=y_sc_c, orientation="vertical", tick_format="d", num_ticks=5
                ),
            ],
            title="Aktuální kapacity",
            layout={"height": "250px", "width": "98%"},
        )

        fig_s = Figure(
            marks=[self._summary_lines],
            axes=[
                Axis(scale=x_sc, label="Čas (min)"),
                Axis(scale=y_sc_s, orientation="vertical"),
            ],
            title="Kumulativní statistiky",
            layout={"height": "250px", "width": "98%"},
        )

        # Zobrazení v požadovaném pořadí
        display(ipw.VBox([fig_q, fig_c, fig_s]))
        self._figs = [fig_q, fig_c, fig_s]

    def append(self, **kwargs):
        self._log.append(kwargs)

        
        if self._queue_lines:
            df = pd.DataFrame(self._log)

            # Update Fronty + Sedadla# konstantní pole s kapacitou stolů
            tables_capacity_line = [self._total_table_capacity] * len(df)

            self._queue_lines.x = df["time"].values
            self._queue_lines.y = [
                df["cashier_queue"].values,
                df["barista_queue"].values,
                df["seats_occupied"].values,
                tables_capacity_line,
            ]

            # Update Kapacity
            self._capacity_lines.x = df["time"].values
            self._capacity_lines.y = [
                df["cap_cashier"].values,
                df["cap_barista"].values,
            ]

            # Update Statistiky
            self._summary_lines.x = df["time"].values
            self._summary_lines.y = [df["served"].values, df["reneged"].values]

    def close(self):
        for f in self._figs:
            f.close()
        self._figs = []


class ResourceManager:
    """Spravuje zdroje s časově závislými kapacitami."""

    def __init__(self, env, config):
        self.env = env
        self.config = config
        self.resources = {}

        if hasattr(config, "used_resources"):
            for rid_str, rnode in config.used_resources.items():
                if rid_str == "label" or str(rid_str).startswith("_"):
                    continue

                rid = int(rid_str)

                # Získej počáteční kapacitu v čase env.now
                initial_cap = self._get_capacity_at_time(rnode, env.now)
                self.resources[rid] = simpy.Resource(env, capacity=initial_cap)

    def _get_capacity_at_time(self, rnode, current_time):
        """
        Zjistí kapacitu zdroje v daném čase.
        Prochází capacity_counts a hledá odpovídající časový rozsah.
        """
        if not hasattr(rnode, "capacity_counts"):
            # Fallback - pokud nejsou definovány směny
            if hasattr(rnode, "capacity"):
                return int(rnode.capacity.value)
            return 1

        # Projdi všechny směny
        for shift_id_str, shift_node in rnode.capacity_counts.items():
            if shift_id_str == "label" or str(shift_id_str).startswith("_"):
                continue

            if not hasattr(shift_node, "time_range"):
                continue

            # Zjisti časový rozsah směny
            time_range = shift_node.time_range.metadata["range"]
            start, end = time_range[0], time_range[1]

            # Pokud je current_time v tomto rozsahu
            if start <= current_time < end:
                # Vrať kapacitu pro tuto směnu
                count = shift_node.capacity_count.value

                # Celková kapacita = počet jednotek × kapacita každé
                unit_capacity = (
                    rnode.capacity.value if hasattr(rnode, "capacity") else 1
                )

                return int(count * unit_capacity)

        # Pokud nejsme v žádné směně, vrať 0 nebo fallback
        return 0

    def update_capacities(self, now):
        """
        Aktualizuje kapacity zdrojů podle aktuálního času simulace.
        Volá se periodicky z _monitor().
        """
        if not hasattr(self.config, "used_resources"):
            return

        for rid_str, rnode in self.config.used_resources.items():
            if rid_str == "label" or str(rid_str).startswith("_"):
                continue

            rid = int(rid_str)
            new_cap = self._get_capacity_at_time(rnode, now)

            # Změna kapacity v SimPy
            if rid in self.resources and self.resources[rid].capacity != new_cap:
                diff = new_cap - self.resources[rid].capacity
                self.resources[rid]._capacity = new_cap

                # Pokud se kapacita zvýšila, aktivuj čekající requesty
                if diff > 0:
                    self.resources[rid]._trigger_put(None)


class TableManager:
    """Spravuje stoly s různými kapacitami a sdílením."""

    def __init__(self, env, config):
        self.env = env
        self.config = config
        self.tables = []  # List of {'id': X, 'capacity': C, 'resource': Resource}

        if hasattr(config, "tables"):
            table_id = 0
            for tid_str, tnode in config.tables.items():
                if tid_str == "label" or str(tid_str).startswith("_"):
                    continue

                capacity = tnode.table_capacity.value
                count = tnode.tables_count.value

                # Vytvoř 'count' stolů s danou kapacitou
                for _ in range(count):
                    table_resource = simpy.Resource(env, capacity=capacity)
                    self.tables.append(
                        {
                            "id": table_id,
                            "capacity": capacity,
                            "resource": table_resource,
                        }
                    )
                    table_id += 1

    def get_total_capacity(self):
        """Vrací celkový počet všech míst (kapacitu)."""
        return sum(t["capacity"] for t in self.tables)

    def get_available_seats(self):
        """
        Vrací info o volných místech u všech stolů.

        Vrací: list of {'table_id': X, 'capacity': C, 'available': A}
        """
        availability = []
        for table in self.tables:
            res = table["resource"]
            available = table["capacity"] - res.count  # Volná místa
            availability.append(
                {
                    "table_id": table["id"],
                    "capacity": table["capacity"],
                    "available": available,
                }
            )
        return availability

    def find_best_table_combination(self, group_size):
        """
        Najde optimální kombinaci stolů pro skupinu.

        Algoritmus (greedy):
        1. Kontrola, zda je dostatek volných míst
        2. Výběr od největších volných míst
        3. Kontrola samotářů (1 osoba u stolu)

        Args:
            group_size: počet osob ve skupině

        Vrací: list of {'table_id': X, 'seats_needed': N} nebo None
        """
        availability = self.get_available_seats()

        # Filtruj stoly s volnými místy
        available_tables = [t for t in availability if t["available"] > 0]

        if not available_tables:
            return None

        # Celkový počet volných míst
        total_available = sum(t["available"] for t in available_tables)

        if total_available < group_size:
            return None

        # Greedy: vezmi stoly od největších volných míst
        available_tables.sort(key=lambda x: x["available"], reverse=True)

        allocation = []
        remaining = group_size

        for table in available_tables:
            if remaining <= 0:
                break

            # Kolik míst u tohoto stolu použijeme?
            seats_to_use = min(remaining, table["available"])

            # Kontrola samotáře: pokud by zbyl 1 člověk a je více míst
            if remaining > seats_to_use and seats_to_use == 1:
                # Radši vezmi 2 místa (pokud jsou k dispozici)
                if table["available"] >= 2:
                    seats_to_use = 2

            allocation.append(
                {"table_id": table["table_id"], "seats_needed": seats_to_use}
            )

            remaining -= seats_to_use

        if remaining > 0:
            return None

        return allocation

    def request_tables(self, allocation):
        """
        Requestuje místa podle alokace.

        Args:
            allocation: list of {'table_id': X, 'seats_needed': N}

        Vrací: list of (table_resource, [requests])
        """
        all_requests = []

        for alloc in allocation:
            table = self.tables[alloc["table_id"]]
            resource = table["resource"]

            # Request 'seats_needed' míst
            requests = []
            for _ in range(alloc["seats_needed"]):
                req = resource.request()
                requests.append(req)

            all_requests.append((resource, requests))

        return all_requests

    def release_tables(self, table_requests):
        """
        Uvolní všechna requestovaná místa.

        Args:
            table_requests: list of (table_resource, [requests])
        """
        for resource, requests in table_requests:
            for req in requests:
                resource.release(req)

    def get_total_occupied(self):
        """Vrací celkový počet obsazených míst."""
        return sum(t["resource"].count for t in self.tables)


# =================================================================
# 2. HLAVNÍ TŘÍDA SIMULACE
# =================================================================


class CafeSimulation:
    def __init__(self, config_path="sim_config.yaml"):
        self._config = ConfigurationManager.load_yaml(config_path)
        self._output_area = ipw.Output()
        self._status_log = None
        self._pbar = None

    # ============================================================
    # POMOCNÉ METODY - Generování a vzorkování
    # ============================================================

    def _sample_distribution(self, param_node):
        """Univerzální vzorkování z distribuce."""
        if not hasattr(param_node, "metadata"):
            return 0.0

        dist = param_node.metadata.get("dist", {})
        dist_type = dist.get("type", "lognormvariate")

        if dist_type == "lognormvariate":
            desired_mean = dist["mean"]["value"]
            desired_std = dist["std"]["value"]

            if desired_std < 0.001:
                return desired_mean

            variance = desired_std**2
            mean_squared = desired_mean**2

            mu = math.log(mean_squared / math.sqrt(mean_squared + variance))
            sigma = math.sqrt(math.log(1 + variance / mean_squared))

            return random.lognormvariate(mu, sigma)

        elif dist_type == "bernoulli":
            p = dist["p"]["value"]
            return 1 if random.random() < p else 0

        return 0.0

    def _bernoulli(self, p):
        """Bernoulliho rozdělení."""
        return random.random() < p

    def _select_customer_type(self, interval_node):
        """Z intervalu vybere typ zákazníka podle vah."""
        mix = interval_node.customer_mix.value

        ids = [int(k) for k in mix.keys()]
        weights = [float(v) for v in mix.values()]

        return random.choices(ids, weights=weights)[0]

    def _generate_group_parameters(self, customer_type_id):
        """Vygeneruje všechny parametry pro skupinu."""
        ctype_node = self._config.customer_types.__dict__.get(str(customer_type_id))

        size = int(max(1, round(self._sample_distribution(ctype_node.group_size))))
        patience = self._sample_distribution(ctype_node.queue_patience)
        wants_table = bool(self._sample_distribution(ctype_node.wants_table))
        consumption_modifier = self._sample_distribution(
            ctype_node.consumption_speed_modifier
        )

        return {
            "size": size,
            "patience": patience,
            "wants_table": wants_table,
            "consumption_modifier": consumption_modifier,
        }

    def _select_categories(self, customer_type_id):
        """Vybere kategorie pomocí Bernoulliho s pojistkou."""
        ctype_node = self._config.customer_types.__dict__.get(str(customer_type_id))
        cat_weights = ctype_node.order_categories_preferences.value

        total_weight = sum(float(w) for w in cat_weights.values())

        if total_weight == 0:
            return []

        selected_categories = []

        for cat_id_str, weight in cat_weights.items():
            probability = float(weight) / total_weight

            if self._bernoulli(probability):
                selected_categories.append(int(cat_id_str))

        # POJISTKA
        if not selected_categories:
            max_cat_id = max(cat_weights.items(), key=lambda x: float(x[1]))[0]
            selected_categories = [int(max_cat_id)]

        return selected_categories

    def _select_item_from_category(self, category_id):
        """Z kategorie vybere položku podle vah."""
        cat_node = self._config.item_categories.__dict__.get(str(category_id))
        item_weights = cat_node.items_weights.value

        ids = [int(k) for k in item_weights.keys()]
        weights = [float(v) for v in item_weights.values()]

        return random.choices(ids, weights=weights)[0]

    def _create_order_for_customer(self, customer_type_id):
        """Vytvoří kompletní objednávku pro jednoho zákazníka."""
        order = []

        selected_categories = self._select_categories(customer_type_id)

        for category_id in selected_categories:
            item_id = self._select_item_from_category(category_id)
            order.append(item_id)

        return order

    def _get_category_for_item(self, item_id):
        """Najde kategorii, do které položka patří."""
        for cat_id_str, cat_node in self._config.item_categories.items():
            if cat_id_str == "label" or str(cat_id_str).startswith("_"):
                continue

            item_weights = cat_node.items_weights.value

            if item_id in [int(k) for k in item_weights.keys()]:
                return int(cat_id_str)

        return None

    def _calculate_consumption_time(self, order):
        """
        Spočítá čas konzumace pro jednoho zákazníka.
        Vrací MAX z časů jednotlivých kategorií.
        """
        if not order:
            return 0.0

        max_time = 0.0

        for item_id in order:
            category_id = self._get_category_for_item(item_id)

            if category_id:
                cat_node = self._config.item_categories.__dict__.get(str(category_id))
                consumption_time = self._sample_distribution(cat_node.consumption_time)
                max_time = max(max_time, consumption_time)

        return max_time

    # ============================================================
    # SIMPY PROCESY
    # ============================================================

    def _process_order_at_cashier(self, group_size):
        """
        Proces přijetí objednávky u pokladny.
        Pro každého člena skupiny vzorkuje čas samostatně.

        Yields SimPy events.
        """
        order_proc = self._config.order_process
        cashier_id = 3  # ID pokladního

        if cashier_id not in self._res_man.resources:
            print(f"VAROVÁNÍ: Pokladní (ID {cashier_id}) neexistuje!")
            return

        cashier = self._res_man.resources[cashier_id]

        with cashier.request() as req:
            yield req

            # Pro každého člena skupiny vzorkuj čas
            total_time = 0
            for _ in range(group_size):
                member_time = self._sample_distribution(order_proc.order_process_time)
                total_time += member_time

            yield self._env.timeout(total_time)

    def _prepare_item(self, item_id):
        """
        Generator pro přípravu jedné položky podle receptu.
        Kroky probíhají SEKVENČNĚ.

        Yields SimPy events.
        """
        menu_item = self._config.menu_items.__dict__.get(str(item_id))

        if not menu_item or not hasattr(menu_item, "recipe"):
            return

        # Získej všechny kroky a seřaď podle ID
        recipe_steps = []
        for step_id_str, step_node in menu_item.recipe.items():
            if step_id_str == "label" or str(step_id_str).startswith("_"):
                continue
            recipe_steps.append((int(step_id_str), step_node))

        recipe_steps.sort(key=lambda x: x[0])

        # Proveď kroky SEKVENČNĚ
        for step_id, step_node in recipe_steps:
            if not hasattr(step_node, "task_used_resources"):
                continue

            resources_needed = step_node.task_used_resources.value
            duration = self._sample_distribution(step_node.recipe_time)

            # Request všechny potřebné zdroje
            requests = []
            for res_id_str, count_needed in resources_needed.items():
                res_id = int(res_id_str)

                if res_id not in self._res_man.resources:
                    continue

                resource = self._res_man.resources[res_id]

                for _ in range(int(count_needed)):
                    req = resource.request()
                    requests.append((resource, req))

            # Čekej na všechny zdroje
            if requests:
                yield simpy.events.AllOf(self._env, [req for _, req in requests])

            # Zpracování
            yield self._env.timeout(duration)

            # Uvolnění zdrojů
            for resource, req in requests:
                resource.release(req)

    def _try_get_tables(self, group_size, patience):
        """
        Pokusí se získat stoly pro skupinu.

        Args:
            group_size: počet osob
            patience: jak dlouho čekat

        Yields SimPy events.
        Vrací: table_requests nebo None
        """
        # Najdi nejlepší kombinaci stolů
        allocation = self._table_man.find_best_table_combination(group_size)

        if allocation is None:
            return None

        # Request místa
        table_requests = self._table_man.request_tables(allocation)

        # Čekej na všechna místa (s timeout)
        all_reqs = []
        for _, reqs in table_requests:
            all_reqs.extend(reqs)

        result = yield simpy.events.AllOf(self._env, all_reqs) | self._env.timeout(
            patience
        )

        # Zkontroluj, zda jsme dostali všechna místa
        if not all(req.triggered for req in all_reqs):
            # Timeout - uvolni co máme
            self._table_man.release_tables(table_requests)
            return None

        return table_requests

    def _group_process(self, customer_type_id):
        """
        Kompletní proces skupiny zákazníků.
        """
        self._groups += 1

        # 1. VYGENERUJ PARAMETRY SKUPINY
        params = self._generate_group_parameters(customer_type_id)

        group_size = params["size"]
        patience = params["patience"]
        wants_table = params["wants_table"]
        consumption_modifier = params["consumption_modifier"]

        # 2. PROCES U POKLADNY
        yield from self._process_order_at_cashier(group_size)

        # 3. GENEROVÁNÍ OBJEDNÁVEK (teprve po pokladně)
        all_orders = []
        customer_consumption_times = []

        for _ in range(group_size):
            order = self._create_order_for_customer(customer_type_id)
            all_orders.append(order)

            # Spočítej čas konzumace
            customer_time = self._calculate_consumption_time(order)
            customer_consumption_times.append(customer_time)

        # Skupina čeká na nejpomalejšího
        group_consumption_time = (
            max(customer_consumption_times) if customer_consumption_times else 0
        )

        # 4. PŘÍPRAVA OBJEDNÁVEK
        for order in all_orders:
            for item_id in order:
                yield from self._prepare_item(item_id)

        # 5. SEDADLA - pokud chtějí a mají co konzumovat
        if wants_table and group_consumption_time > 0:
            table_result = yield from self._try_get_tables(group_size, patience)

            if table_result:
                # Máme stůl - konzumace
                adjusted_time = group_consumption_time * consumption_modifier
                yield self._env.timeout(adjusted_time)

                # Uvolnění stolu
                self._table_man.release_tables(table_result)

                self._served += group_size
            else:
                # Nepodařilo se získat stůl
                self._reneged += group_size
        else:
            # Nechtějí stůl nebo nemají co konzumovat
            self._served += group_size

    def _customer_generator(self):
        """Generátor zákazníků podle časových intervalů."""

        # Získej všechny intervaly
        intervals = []
        for iid, inode in self._config.time_intervals.items():
            if iid == "label" or str(iid).startswith("_"):
                continue
            start, end = inode.time_range.metadata["range"]
            intervals.append((start, end, inode))

        # Seřaď podle času
        intervals.sort(key=lambda x: x[0])

        if not intervals:
            return

        # Skoč na začátek prvního intervalu
        first_start = intervals[0][0]
        if self._env.now < first_start:
            yield self._env.timeout(first_start - self._env.now)

        # Procházej intervaly
        for start, end, inode in intervals:
            # Skoč na začátek intervalu
            if self._env.now < start:
                yield self._env.timeout(start - self._env.now)

            arrival_rate = inode.arrival_rate.value

            # Generuj zákazníky dokud neskončí interval
            while self._env.now < end:
                # Vyber typ zákazníka
                ctype_id = self._select_customer_type(inode)

                if ctype_id:
                    # Spusť proces pro tuto skupinu
                    self._env.process(self._group_process(ctype_id))

                # Čekej na dalšího zákazníka (exponenciální rozdělení)
                interarrival = random.expovariate(arrival_rate / 60.0)
                yield self._env.timeout(interarrival)

    def _monitor(self):
        yield self._env.timeout(0)
        last_time = self._env.now

        while True:
            # Aktualizace kapacit v ResourceManageru
            self._res_man.update_capacities(self._env.now)

            # Update progress baru
            if self._pbar:
                self._pbar.update(self._env.now - last_time)
            last_time = self._env.now

            # Počet obsazených sedadel
            seats_occupied = (
                self._table_man.get_total_occupied() if self._table_man else 0
            )

            # Fronty u zdrojů
            q_cashier = (
                len(self._res_man.resources[3].queue)
                if 3 in self._res_man.resources
                else 0
            )
            q_barista = (
                len(self._res_man.resources[4].queue)
                if 4 in self._res_man.resources
                else 0
            )

            # Kapacity zdrojů
            c_cashier = (
                self._res_man.resources[3].capacity
                if 3 in self._res_man.resources
                else 0
            )
            c_barista = (
                self._res_man.resources[4].capacity
                if 4 in self._res_man.resources
                else 0
            )

            self._status_log.append(
                time=self._env.now,
                cashier_queue=q_cashier,
                barista_queue=q_barista,
                seats_occupied=seats_occupied,
                cap_cashier=c_cashier,
                cap_barista=c_barista,
                served=self._served,
                reneged=self._reneged,
            )

            yield self._env.timeout(1)
            time.sleep(0.02)

    # ============================================================
    # HLAVNÍ METODY
    # ============================================================

    def _get_simtime_interval(self):
        intervals = self._config.time_intervals
        all_times = []
        for k, v in intervals.items():
            if k != "label":
                all_times.extend(v.time_range.metadata["range"])

        start_time = min(all_times) if all_times else 0
        end_time = max(all_times) if all_times else 1440

        return start_time, end_time

    def run(self, b=None):
        if b:
            b.disabled = True

        start_time, end_time = self._get_simtime_interval()
        duration = end_time - start_time

        with self._output_area:
            clear_output(wait=True)

            if self._status_log:
                self._status_log.close()

            if self._pbar:
                self._pbar.close()
                self._pbar = None

            self._env = simpy.Environment()

            if start_time > 0:
                self._env.run(until=start_time)

            # Inicializace managerů
            self._res_man = ResourceManager(self._env, self._config)
            self._table_man = TableManager(self._env, self._config)

            total_table_capacity = self._table_man.get_total_capacity()

            self._status_log = StatusLog(
                min_time=start_time,
                max_time=end_time,
                total_table_capacity=total_table_capacity,
            )

            self._served = 0
            self._reneged = 0
            self._groups = 0

            self._status_log.show()

            # Počáteční stav pro grafy
            self._status_log.append(
                time=self._env.now,
                cashier_queue=0,
                barista_queue=0,
                seats_occupied=0,
                cap_cashier=(
                    self._res_man.resources[3].capacity
                    if 3 in self._res_man.resources
                    else 0
                ),
                cap_barista=(
                    self._res_man.resources[4].capacity
                    if 4 in self._res_man.resources
                    else 0
                ),
                served=0,
                reneged=0,
            )

            self._pbar = tqdm(
                total=int(duration),
                initial=int(start_time),
                desc="Průběh dne",
                leave=False,
            )

            # Spuštění procesů
            self._env.process(self._customer_generator())
            self._env.process(self._monitor())

            self._env.run(until=end_time)
            self._pbar.close()
            print(f"\n--- HOTOVO ---")
            print(f"Obslouženo: {self._served}, Odešlo: {self._reneged}")

        if b:
            b.disabled = False

    def create_ui(self):
        from sim_configuration import ConfigUIBuilder

        ui_builder = ConfigUIBuilder(self._config)
        run_btn = ipw.Button(description="▶ Spustit", button_style="success")
        save_btn = ipw.Button(description="💾 Uložit", button_style="info")
        run_btn.on_click(self.run)
        save_btn.on_click(
            lambda b: ConfigurationManager.save_yaml(self._config, "sim_config.yaml")
        )

        display(
            ipw.VBox(
                [
                    ipw.HTML("<h2>☕ Nastavení a Start</h2>"),
                    ui_builder.create_ui(self._config),
                    ipw.HBox([run_btn, save_btn], layout=ipw.Layout(margin="10px 0")),
                    self._output_area,
                ]
            )
        )


# --- Spuštění v notebooku ---
if __name__ == "__main__":
    sim = CafeSimulation("sim_config.yaml")
    sim.create_ui()
