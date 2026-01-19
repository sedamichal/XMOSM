import os
from abc import ABC, abstractmethod
import yaml
from IPython.display import display, clear_output
import ipywidgets as ipw


class CafeSimulationConfig(ABC):
    _config = {}
    _ui_elements = {}

    def __init__(self, yaml_file: str | None = None):
        self._yaml_file = yaml_file if yaml_file != None else self.get_default_yaml()
        self._load_yaml()

    def get_default_yaml(self):
        # Cesta k adresáři, kde leží tento .py soubor
        script_dir = os.path.dirname(os.path.abspath(__file__))
        yaml_path = os.path.join(script_dir, self._default_yaml_name())
        return yaml_path

    def _default_yaml_name(self):
        return "default_config.yaml"

    def __getitem__(self, key: str):
        item = self._ui_elements[key]
        return item.value

    def _load_yaml(self):
        with open(self._yaml_file, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)

    def _create_section(self, section_key):
        items = []

        for key, params in self._config.get(section_key).items():
            if key == "label":
                continue

            widget_class = getattr(ipw, params["type"])

            w = widget_class(
                value=params["default"],
                min=params["min"],
                max=params["max"],
                step=params.get("step", 1),
                description=params["label"],
                style={"description_width": "250px"},
                layout=ipw.Layout(width="500px"),
            )

            self._ui_elements[key] = w
            items.append(w)

        return ipw.VBox(items)

    @property
    def drinks(self):
        drink_section = self._config.get("drink_wait")
        return [key for key in drink_section if key != "label"]

    def create_ui(self):
        self._ui_elements = {}
        containers = []
        descriptions = []

        for key in self._config.keys():
            containers.append(self._create_section(key))
            section = self._config.get(key)
            if "label" in section:
                descriptions.append(section["label"])
            else:
                descriptions.append(key)

        accordion = ipw.Accordion(children=containers)
        for i, desc in enumerate(descriptions):
            accordion.set_title(i, desc)

        display(accordion)

        self._create_save_button()

    def _create_save_button(self):
        save_btn = ipw.Button(
            description="Uložit do YAML",
            button_style="success",  # Zelené tlačítko
            icon="save",
        )

        # 3. Definujeme akci po kliknutí
        def on_save_clicked(b):
            self.save_ui()

        save_btn.on_click(on_save_clicked)

        # 4. Zobrazíme tlačítko pod slidery
        display(save_btn)

    @abstractmethod
    def save_ui(self):
        pass


class CafeSimulationConfigUS(CafeSimulationConfig):

    def _default_yaml_name(self):
        return "us_default_config.yaml"

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
