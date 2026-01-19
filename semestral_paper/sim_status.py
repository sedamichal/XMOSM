from enum import Enum

import numpy as np
import pandas as pd
import yaml
import matplotlib.pyplot as plt
from IPython.display import display, clear_output
import ipywidgets as ipw
from ipywidgets import interact, interactive, fixed, interact_manual


class SimulationStatus:
    _stats = {}

    def __init__(self, enum_stats: type[Enum]):
        self._enum_class = enum_stats
        self._set_stats()

    def __getitem__(self, key):
        if not isinstance(key, self._enum_class):
            raise TypeError(f"Očekáván {self._enum_class}, dostal jsem {type(key)}")

        return self._stats[key]

    def __setitem__(self, key, value):
        if not isinstance(key, self._enum_class):
            raise TypeError(f"Očekáván {self._enum_class}, dostal jsem {type(key)}")

        self._stats[key] = value

    def reset(self):
        self._stats = {}
        self._stats = {event: [] for event in self._enum_class}
