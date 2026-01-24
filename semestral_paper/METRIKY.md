# Metriky simulace - Dokumentace

## Přehled dostupných metrik

Simulace nyní automaticky sbírá a vypočítává následující metriky:

### 📊 Celkové statistiky

| Metrika | Popis | Jednotka |
|---------|-------|----------|
| `total_served` | Celkový počet obsloužených zákazníků | počet |
| `total_reneged` | Celkový počet zákazníků, kteří odešli | počet |
| `total_customers` | Celkový počet příchozích zákazníků | počet |
| `success_rate` | Úspěšnost obsluhy | % |

### 📈 Fronty

| Metrika | Popis | Jednotka |
|---------|-------|----------|
| `avg_cashier_queue` | Průměrná délka fronty u pokladny | skupiny |
| `max_cashier_queue` | Maximální délka fronty u pokladny | skupiny |
| `avg_barista_queue` | Průměrná délka fronty u baristu | skupiny |
| `max_barista_queue` | Maximální délka fronty u baristu | skupiny |

### 🪑 Stoly

| Metrika | Popis | Jednotka |
|---------|-------|----------|
| `avg_seats_occupied` | Průměrné obsazení stolů | místa |
| `max_seats_occupied` | Maximální obsazení stolů | místa |
| `avg_seats_utilization` | Průměrné využití kapacity stolů | % |

### ⚙️ Využití zdrojů

| Metrika | Popis | Jednotka |
|---------|-------|----------|
| `avg_cashier_utilization` | Průměrné využití pokladny | % |
| `avg_barista_utilization` | Průměrné využití baristy | % |

**Poznámka:** Metriky se počítají po warmup periodě (první hodině), aby se eliminoval vliv inicializace.

---

## Použití v kódu

### Základní použití

```python
from sim_cafe import CafeSimulation

# Spustit simulaci
sim = CafeSimulation("sim_config.yaml")
sim.run()  # Automaticky zobrazí metriky na konci

# Získat metriky jako dict
metrics = sim.get_last_metrics()
print(metrics['success_rate'])  # např. 87.5

# Získat časovou řadu jako DataFrame
data = sim.get_last_data()
print(data.head())
```

### Vícenásobné běhy (Monte Carlo)

```python
import pandas as pd

results = []
for i in range(10):
    sim = CafeSimulation("sim_config.yaml")
    sim.run()
    
    metrics = sim.get_last_metrics()
    metrics['run_id'] = i
    results.append(metrics)

# Analýza
df = pd.DataFrame(results)
print(df['success_rate'].mean())  # Průměr z 10 běhů
print(df['success_rate'].std())   # Směrodatná odchylka
```

### Porovnání scénářů

```python
scenarios = {
    'Baseline': 'sim_config.yaml',
    'More Baristas': 'sim_config_baristas.yaml',
    'More Tables': 'sim_config_tables.yaml'
}

comparison = []
for name, config in scenarios.items():
    sim = CafeSimulation(config)
    sim.run()
    
    metrics = sim.get_last_metrics()
    metrics['scenario'] = name
    comparison.append(metrics)

df = pd.DataFrame(comparison)
print(df[['scenario', 'success_rate', 'total_reneged']])
```

### Export pro další analýzu

```python
# Export metrik
metrics = sim.get_last_metrics()
pd.DataFrame([metrics]).to_csv('metrics.csv', index=False)

# Export časové řady
timeseries = sim.get_last_data()
timeseries.to_csv('timeseries.csv', index=False)
```

---

## Výstup na konzoli

Po spuštění simulace se automaticky zobrazí:

```
============================================================
SOUHRNNÉ METRIKY SIMULACE
============================================================

📊 CELKOVÉ STATISTIKY:
  Celkem příchozích:       560
  Obslouženo:              487 ( 87.0%)
  Odešlo (reneged):         73 ( 13.0%)

📈 FRONTY:
  Pokladna:
    Průměrná délka:       1.82 skupin
    Maximální délka:         8 skupin
  Barista:
    Průměrná délka:       2.34 skupin
    Maximální délka:        12 skupin

🪑 STOLY:
  Průměrné obsazení:      18.5 míst ( 46.2%)
  Maximální obsazení:       38 míst
  Celková kapacita:         40 míst

⚙️  VYUŽITÍ ZDROJŮ:
  Pokladna:               91.0%
  Barista:                117.0%
============================================================
```

---

## Poznámky k interpretaci

### Využití zdrojů > 100%?

Ano, je to možné! Využití zdrojů = průměrná fronta / kapacita × 100%.

- **< 100%** = Zdroj není plně vytížen (má volnou kapacitu)
- **≈ 100%** = Zdroj je optimálně vytížen
- **> 100%** = Zdroj je přetížen (tvoří se fronty)

Například: Barista s kapacitou 2 a průměrnou frontou 2.34 = 117% vytížení = PŘETÍŽEN

### Warmup perioda

První hodina simulace (60 minut) se ignoruje při výpočtu průměrů, protože:
- Systém se stabilizuje
- Fronty se teprve tvoří
- Nevypovídá o ustáleném chování

### Success rate vs. Service level

- **Success rate** = Kolik zákazníků bylo obslouženo (bez ohledu na čekání)
- **Service level** = Kolik zákazníků bylo obslouženo RYCHLE (obvykle s max. čekáním)

Simulace aktuálně měří success rate. Service level by vyžadoval sledování čekacích dob.

---

## Rozšíření metrik

Pokud chcete přidat vlastní metriky, upravte metodu `get_metrics()` v `StatusLog`:

```python
def get_metrics(self):
    # ... existující kód ...
    
    # Přidat novou metriku
    metrics['custom_metric'] = ... výpočet ...
    
    return metrics
```

---

## Viz také

- `experiment_examples.py` - Kompletní příklady experimentů
- `sim_cafe.py` - Hlavní implementace
- `semestral_report.md` - Semestrální práce s analýzou
