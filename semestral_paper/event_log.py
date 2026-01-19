import pandas as pd

class EventLog:
    _instance = None

    def __new__(cls):
        if cls._instance == None:
            cls._instance = super(EventLog, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self._events = []

    def log(self, time, event_type, **kwargs):
        """Uloží záznam o události."""
        entry = {
            "time": time,
            "event_type": event_type,
            **kwargs,  # Rozbalí data přímo do slovníku pro snazší export do CSV/Pandas
        }
        self._events.append(entry)

    def to_dataframe(self):
        """Převede log na Pandas DataFrame."""
        return pd.DataFrame(self._events)

    def get_summary(self):
        """Vrátí základní počty událostí podle typu."""
        df = self.to_dataframe()
        if df.empty:
            return "Log je prázdný."
        return df["event_type"].value_counts()
