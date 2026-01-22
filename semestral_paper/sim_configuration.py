import yaml
import random
import ipywidgets as ipw
from IPython.display import display

# =================================================================
# POMOCNÉ FUNKCE
# =================================================================


def seconds_to_hms(total_minutes):
    if total_minutes is None:
        return "0s"
    total_seconds = int(round(total_minutes * 60))
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    if h > 0:
        return f"{h:d}:{m:02d}:{s:02d}"
    if m > 0:
        return f"{m:02d}:{s:02d}"
    return f"{s:d}s"


# =================================================================
# 1. JÁDRO: STRUKTURA KONFIGURACE
# =================================================================


class ConfigParam:
    def __init__(self, data):
        self.metadata = data
        self.type = "unknown"
        self.map_key = None

        if "dist" in data:
            self.type = "dist"
        elif "section" in data:
            # Má explicitní section -> section_map
            self.type = "section_map"
            for key in data:
                if key not in ["section", "label"] and isinstance(data[key], dict):
                    self.map_key = key
                    # self.value = data[key]
                    break
        elif "range" in data:
            self.type = "range"
        elif "value" in data:
            self.type = "simple"
        elif "weights" in data:
            # weights bez section
            self.type = "section_map"
            self.map_key = "weights"
            # self.value = data["weights"]
        elif "resources" in data:
            # resources bez section
            self.type = "section_map"
            self.map_key = "resources"
            # self.value = data["resources"]

        # if self.type == "simple":
        #     self.value = data.get("value")

    @property
    def value(self):
        """Tento getter zajistí, že simulace dostane vždy aktuální data z metadat."""
        if self.type == "simple":
            return self.metadata.get("value")
        if self.type == "section_map":
            return self.metadata.get(self.map_key, {})
        return None

    def update(self, new_val):
        if "value" in self.metadata:
            if isinstance(self.metadata["value"], int):
                new_val = int(round(new_val))
            else:
                new_val = round(new_val, 4)
            self.metadata["value"] = new_val


class ConfigNode:
    def __init__(self, data, default_label=""):
        self._fallback_label = default_label
        for key, value in data.items():
            str_key = str(key)
            if isinstance(value, dict):
                if any(k in value for k in ["value", "dist", "section", "range"]):
                    setattr(self, str_key, ConfigParam(value))
                elif "weights" in value or "resources" in value:
                    # POUZE pokud má explicitně weights nebo resources
                    setattr(self, str_key, ConfigParam(value))
                else:
                    # Běžný ConfigNode
                    setattr(
                        self,
                        str_key,
                        ConfigNode(value, default_label=value.get("label", "")),
                    )
            else:
                setattr(self, str_key, value)

    def get_label(self):
        label_attr = getattr(self, "label", None)
        return (
            label_attr
            if (label_attr and isinstance(label_attr, str))
            else self._fallback_label
        )

    def items(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}.items()

    def to_dict(self):
        result = {}
        for key, value in self.items():
            if isinstance(value, ConfigNode):
                result[key] = value.to_dict()
            elif isinstance(value, ConfigParam):
                if value.type == "section_map":
                    meta_copy = value.metadata.copy()
                    map_key = value.map_key
                    if map_key:
                        meta_copy[map_key] = {
                            (int(k) if str(k).isdigit() else k): v
                            for k, v in value.metadata[map_key].items()
                            if v > 0
                        }
                    result[key] = meta_copy
                else:
                    result[key] = value.metadata
            else:
                result[key] = value
        return {int(k) if str(k).isdigit() else k: v for k, v in result.items()}


# =================================================================
# 2. UI BUILDER
# =================================================================


class ConfigUIBuilder:
    def __init__(self, root_node):
        self.root = root_node

    def find_pattern(self, path_parts):
        """Hledá pattern v root.patterns podle cesty, ignoruje ID a technické uzly."""
        if not hasattr(self.root, "patterns"):
            return {}

        # Očistíme cestu od čísel (ID)
        clean_path = [str(p) for p in path_parts if not str(p).isdigit()]

        patterns_obj = self.root.patterns
        current = patterns_obj
        found_path = []
        started = False

        i = 0
        while i < len(clean_path):
            part = clean_path[i]

            if not started:
                # Hledáme začátek v patterns (přeskakujeme sekce jako customer_types)
                if hasattr(patterns_obj, part):
                    current = getattr(patterns_obj, part)
                    found_path = [part]
                    started = True
                i += 1
            else:
                # Už jsme v patterns
                if isinstance(current, ConfigParam):
                    # Jsme v ConfigParam, procházíme jeho metadata jako slovník
                    metadata = current.metadata

                    # Projdeme zbytek cesty přes metadata
                    for remaining_part in clean_path[i:]:
                        if isinstance(metadata, dict) and remaining_part in metadata:
                            metadata = metadata[remaining_part]
                            found_path.append(remaining_part)
                        else:
                            # Nemůžeme pokračovat
                            break

                    # Vrátíme to, co jsme našli
                    if isinstance(metadata, dict):
                        return metadata
                    else:
                        return {}

                elif isinstance(current, ConfigNode):
                    if hasattr(current, part):
                        current = getattr(current, part)
                        found_path.append(part)
                        i += 1
                    else:
                        # Nemůžeme pokračovat po cestě
                        # Zkusme najít pattern přímo pro tuto část
                        if hasattr(patterns_obj, part):
                            current = getattr(patterns_obj, part)
                            found_path = [part]
                            i += 1
                        else:
                            break
                else:
                    break

        # Vrátíme result
        if isinstance(current, ConfigParam):
            return current.metadata
        elif isinstance(current, ConfigNode):
            result = {
                k: v for k, v in current.__dict__.items() if not k.startswith("_")
            }
            return result

        return {}

    def create_ui(self, node, path_prefix=None):
        params_elements, sub_sections_elements, sub_sections_titles = [], [], []
        path_prefix = path_prefix or []

        sorted_keys = sorted(node.__dict__.keys())

        for key in sorted_keys:
            if key.startswith("_") or key == "patterns":
                continue
            item = getattr(node, key)
            current_path = path_prefix + [key]

            if isinstance(item, ConfigParam):
                p_meta = self.find_pattern(current_path)

                if item.type == "range":
                    label = p_meta.get("label", key)
                    range_slider = ipw.IntRangeSlider(
                        value=item.metadata["range"],
                        min=0,
                        max=1440,
                        step=1,
                        description=f"{label}",
                        style={"description_width": "initial"},
                        layout={"width": "98%"},
                    )
                    time_label = ipw.HTML(
                        f"<small>{seconds_to_hms(item.metadata['range'][0])} — {seconds_to_hms(item.metadata['range'][1])}</small>"
                    )

                    def on_ch(change, p=item, lab=time_label):
                        p.metadata["range"] = list(change.new)
                        lab.value = f"<small>{seconds_to_hms(change.new[0])} — {seconds_to_hms(change.new[1])}</small>"

                    range_slider.observe(on_ch, names="value")
                    params_elements.append(
                        ipw.VBox(
                            [ipw.HBox([ipw.Label(label), time_label]), range_slider]
                        )
                    )

                elif item.type == "section_map":
                    label = p_meta.get("label", key)
                    map_min, map_max, map_step = (
                        p_meta.get("min_value", 0.0),
                        p_meta.get("max_value", 1.0),
                        p_meta.get("step", 0.01),
                    )

                    # Získej název mapy a section
                    map_key = item.map_key
                    map_data = item.metadata.get(map_key, {})

                    # Section může být v datech nebo v patternu
                    section_name = item.metadata.get("section") or p_meta.get("section")

                    # NOVÉ: Získej všechna dostupná ID ze zdrojové sekce
                    available_ids = set()
                    if section_name and hasattr(self.root, section_name):
                        section_node = getattr(self.root, section_name)
                        for item_id_str in section_node.__dict__.keys():
                            if (
                                not item_id_str.startswith("_")
                                and item_id_str != "label"
                            ):
                                # Zkus převést na int, pokud je to číselný string
                                try:
                                    available_ids.add(int(item_id_str))
                                except ValueError:
                                    available_ids.add(item_id_str)

                    # Doplň chybějící ID s nulovou hodnotou
                    for aid in available_ids:
                        if aid not in map_data:
                            map_data[aid] = 0
                            # Ulož zpět do metadat
                            item.metadata[map_key][aid] = 0

                    # Seřaď podle ID
                    sorted_ids = sorted(
                        map_data.keys(), key=lambda x: (isinstance(x, str), x)
                    )

                    sliders = []
                    for item_id in sorted_ids:
                        item_val = map_data[item_id]

                        # KONTROLA: Přeskoč, pokud hodnota není číslo
                        if isinstance(item_val, dict):
                            continue

                        try:
                            item_val = float(item_val)
                        except (ValueError, TypeError):
                            continue

                        s = ipw.FloatSlider(
                            value=item_val,
                            min=float(map_min),
                            max=float(map_max),
                            step=float(map_step),
                            description=self._get_label_from_section(
                                section_name, item_id
                            ),
                            style={"description_width": "initial"},
                            layout={"width": "98%"},
                        )

                        def make_cb(iid, p=item, mk=map_key):
                            # DŮLEŽITÉ: Musíme měnit přímo slovník v metadata
                            def update_config(change):
                                p.metadata[mk][iid] = round(change.new, 4)
                            return update_config
                            # return lambda c: p.metadata[mk].update(
                            #     {iid: round(c.new, 4)}
                            # )

                        s.observe(make_cb(item_id), names="value")
                        sliders.append(s)

                    # Zobraz pouze pokud máme nějaké slidery
                    if sliders:
                        params_elements.append(
                            ipw.VBox(
                                [ipw.HTML(f"<b style='font-size: 12px;'>{label}</b>")]
                                + sliders,
                                layout={
                                    "border": "1px solid #ddd",
                                    "padding": "5px",
                                    "margin": "5px 0",
                                },
                            )
                        )

                elif item.type == "dist":
                    label = p_meta.get("label", key)
                    is_time = p_meta.get("quantity") == "time"
                    elements = [ipw.HTML(f"<b style='font-size: 12px;'>{label}</b>")]
                    for p_name, p_data in item.metadata["dist"].items():
                        if isinstance(p_data, dict) and "value" in p_data:
                            # Tady hledáme pattern pro konkrétní mean/std/p
                            sub_p_meta = self.find_pattern(
                                current_path + ["dist", p_name]
                            )
                            elements.append(
                                self._make_slider(
                                    p_data,
                                    f"↳ {p_name}",
                                    sub_p_meta,
                                    force_time=is_time,
                                )
                            )
                    params_elements.append(
                        ipw.VBox(
                            elements,
                            layout={
                                "border": "1px dotted #ccc",
                                "padding": "5px",
                                "margin": "5px 0",
                            },
                        )
                    )

                elif item.type == "simple":
                    params_elements.append(
                        self._make_slider(item.metadata, key, p_meta)
                    )

            elif isinstance(item, ConfigNode):
                sub_sections_elements.append(
                    self.create_ui(item, path_prefix=current_path)
                )

                # Priorita: 1. label z ConfigNode, 2. label z patternu s prefixem, 3. klíč
                node_label = item.get_label()

                if node_label and node_label != "":
                    # ConfigNode má vlastní neprázdný label
                    title = node_label
                else:
                    # Zkus pattern
                    pattern_label = self.find_pattern(current_path).get("label", "")

                    if pattern_label:
                        title = pattern_label
                    else:
                        title = str(key)

                # Přidání prefixu pro ID položky (POUZE pokud nemáme vlastní label)
                if key.isdigit() and not node_label:
                    parent_p = self.find_pattern(path_prefix)
                    prefix = parent_p.get("item_prefix", "")
                    if prefix:
                        title = f"{prefix} {key}"

                sub_sections_titles.append(title)

        res = []
        if params_elements:
            res.append(ipw.VBox(params_elements))
        if sub_sections_elements:
            acc = ipw.Accordion(children=sub_sections_elements)
            for i, t in enumerate(sub_sections_titles):
                acc.set_title(i, t)
            acc.selected_index = None
            res.append(acc)
        return ipw.VBox(res)

    def _make_slider(self, meta_dict, label, p_meta, force_time=False):
        val = meta_dict["value"]

        # Získání mezí z patternu s lepšími fallbacky
        min_v = float(p_meta.get("min_value", 0))

        # Pro max_value: pokud je v patternu, použij ho, jinak inteligentní fallback
        if "max_value" in p_meta:
            max_v = float(p_meta["max_value"])
        else:
            # Fallback pouze pokud pattern neobsahuje max_value
            max_v = float(val * 2 if val != 0 else 100)

        # Ujisti se, že aktuální hodnota je v rozsahu
        if val < min_v:
            val = min_v
            meta_dict["value"] = val
        if val > max_v:
            val = max_v
            meta_dict["value"] = val

        is_time = force_time or p_meta.get("quantity") == "time"
        step_v = float(p_meta.get("step", 0.25 if is_time else 0.1))

        orig_label = p_meta.get("label", label)
        s_class = (
            ipw.IntSlider if (isinstance(val, int) and not is_time) else ipw.FloatSlider
        )

        slider = s_class(
            value=float(val),
            min=min_v,
            max=max_v,
            step=step_v,
            description=(
                f"{orig_label} ({seconds_to_hms(val)})" if is_time else orig_label
            ),
            style={"description_width": "initial"},
            layout={"width": "98%"},
        )

        def on_change(change):
            v = round(change.new / step_v) * step_v
            # Ověř, že hodnota je v mezích
            v = max(min_v, min(v, max_v))
            meta_dict["value"] = v
            if is_time:
                slider.description = f"{orig_label} ({seconds_to_hms(v)})"

        slider.observe(on_change, names="value")
        return slider

    def _get_label_from_section(self, section_name, item_id):
        if not section_name:
            return f"ID {item_id}"
        try:
            return getattr(
                getattr(self.root, str(section_name)), str(item_id)
            ).get_label()
        except:
            return f"ID {item_id}"

    def show_full_dashboard(self, config_node, save_path):
        save_btn = ipw.Button(
            description="Uložit konfiguraci",
            button_style="success",
            icon="save",
            layout={"width": "250px"},
        )
        save_btn.on_click(
            lambda b: ConfigurationManager.save_yaml(config_node, save_path)
        )
        display(
            ipw.VBox(
                [
                    ipw.HTML("<h2 style='color: #2c3e50;'>Konfigurace</h2>"),
                    self.create_ui(config_node),
                    ipw.HTML("<br>"),
                    save_btn,
                ]
            )
        )


class ConfigurationManager:
    @staticmethod
    def load_yaml(path):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return ConfigNode(data)

    @staticmethod
    def save_yaml(config_node, path):
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(
                config_node.to_dict(),
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
        print(f"Uloženo: {path}")
