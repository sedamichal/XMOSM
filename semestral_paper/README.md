# ☕ Simulační model provozu kavárny

Diskrétní simulační model kavárny implementovaný v Pythonu s využitím knihovny SimPy. Projekt vytvořen jako semestrální práce z předmětu Modelování a simulace (MOSIM).

---

## 📋 Obsah projektu

### Hlavní soubory

| Soubor | Popis |
|--------|-------|
| `sim_cafe.py` | ✅ **Hlavní implementace** - kompletní simulační model |
| `sim_configuration.py` | ⚙️ **Konfigurační systém** - YAML parser a UI builder |
| `sim_config.yaml` | 📝 **Konfigurace** - parametry simulace |
| `semestral_report.md` | 📄 **Semestrální práce** - kompletní dokumentace (35 stran) |

### Pomocné soubory

| Soubor | Popis |
|--------|-------|
| `METRIKY.md` | 📊 **Dokumentace metrik** - popis všech dostupných metrik |
| `experiment_examples.py` | 🧪 **Příklady experimentů** - jak provádět analýzy |

---

## 🚀 Rychlý start

### 1. Instalace závislostí

```bash
pip install simpy pandas numpy ipywidgets bqplot tqdm pyyaml --break-system-packages
```

### 2. Spuštění v Jupyter notebooku

```python
from sim_cafe import CafeSimulation

# Vytvoř simulaci
sim = CafeSimulation("sim_config.yaml")

# Zobraz interaktivní UI
sim.create_ui()

# Klikni na "▶ Spustit"
```

### 3. Programové spuštění

```python
# Spuštění bez UI
sim = CafeSimulation("sim_config.yaml")
sim.run()

# Získání metrik
metrics = sim.get_last_metrics()
print(f"Úspěšnost: {metrics['success_rate']:.1f}%")
```

---

## 🎯 Klíčové vlastnosti

### ✅ Realistický model
- **5 typů zákazníků** s různým chováním (ranní spěchající, maminky, důchodci...)
- **Stochastické procesy** - log-normální, exponenciální, Bernoulliho rozdělení
- **Realistická logika** - kontrola stolů PŘED vstupem do fronty
- **Korektní resource management** - uvolňování zdrojů i při timeoutech

### 📊 Bohaté metriky
Po každém běhu automaticky zobrazí:
- 📈 Celkové statistiky (obslouženo, reneged, úspěšnost)
- 🚶 Fronty (průměr, maximum)
- 🪑 Obsazení stolů (průměr, maximum, využití kapacity)
- ⚙️ Využití zdrojů (pokladna, baristé)

### 🎨 Real-time vizualizace
Tři interaktivní grafy:
1. **Fronty a sedadla** - vývoj front + obsazení stolů + kapacita
2. **Kapacity zdrojů** - časově závislé směny
3. **Kumulativní statistiky** - obslouženo vs. reneged

### 🔧 Flexibilní konfigurace
- YAML soubory pro snadnou editaci
- Interaktivní UI s slidery (ipywidgets)
- Časově závislé kapacity (ranní vs. odpolední směna)
- Sekvenční recepty pro položky menu

---

## 🏗️ Architektura

### Hlavní třídy

```
CafeSimulation          # Hlavní řadič simulace
├── ResourceManager     # Správa zdrojů (baristé, kávovary, trouby, pokladny)
├── TableManager        # Správa stolů (alokace, sdílení)
└── StatusLog           # Sběr dat a vizualizace
```

### Proces skupiny zákazníků

```
1. Příchod
2. Generování parametrů (velikost, patience, wants_table)
3. Chce stůl? → Kontrola dostupnosti
   ├─ Není volný → RENEGED
   └─ Je volný → Obsazení
4. Fronta na pokladnu (timeout = patience)
   ├─ Timeout → Uvolnění stolu → RENEGED
   └─ OK → Pokračuj
5. Proces u pokladny
6. Generování objednávek (Bernoulli + weighted choice)
7. Příprava položek (sekvenční kroky)
8. Konzumace u stolu
9. Uvolnění stolu
10. SERVED ✓
```

---

## 🧪 Experimenty

### Základní experiment

```python
sim = CafeSimulation("sim_config.yaml")
sim.run()
metrics = sim.get_last_metrics()
```

### Monte Carlo (více běhů)

```python
results = []
for i in range(10):
    sim = CafeSimulation("sim_config.yaml")
    sim.run()
    results.append(sim.get_last_metrics())

df = pd.DataFrame(results)
print(df['success_rate'].describe())
```

### Porovnání scénářů

```python
scenarios = {
    'Baseline': 'sim_config.yaml',
    'More Baristas': 'sim_config_baristas.yaml',
    'More Tables': 'sim_config_tables.yaml'
}

for name, config in scenarios.items():
    sim = CafeSimulation(config)
    sim.run()
    # Analýza...
```

**Viz `experiment_examples.py` pro kompletní příklady!**

---

## 📊 Ukázka výstupu

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
  Barista:                117.0%  ⚠️ PŘETÍŽEN!
============================================================
```

---

## 🔍 Klíčová zjištění (ze semestrální práce)

### Primární úzké místo: Baristé
- Průměrná fronta: 2.3 skupin
- Maximum: 12 skupin
- **Využití: 117%** → PŘETÍŽENI

**Doporučení:**
- ➕ Přidat 1 baristu na ranní špičku (7:00–11:00)
- 🚀 Zavést "express" menu s jednodušší přípravou
- **Očekávaný efekt:** -40% reneged

### Sekundární problém: Dostupnost stolů
- Obsazenost během oběda: 95%
- Zákazníci kontrolují PŘED vstupem do fronty

**Doporučení:**
- 🪑 Přidat 2–3 malé stoly
- 💰 Dynamic pricing (sleva mimo peak)

---

## 📚 Teoretický základ

Model je založen na teorii **systémů hromadné obsluhy**:

- **Kendallova klasifikace:** M/G/c/K
- **Fronty:** FIFO s timeoutem (patience)
- **Zdroje:** Facility (kapacita 1) a Sklad (kapacita N)
- **Diskrétní simulace:** Události, kalendář, stochastické procesy

**Zdroj:** Janošek, M., Farana, R. (2016). *Modelování a simulace*. Ostravská univerzita.

---

## 🛠️ Technologie

- **Python 3.11+**
- **SimPy 4.x** - diskrétní simulační framework
- **Pandas, NumPy** - zpracování dat
- **bqplot, ipywidgets** - interaktivní vizualizace
- **PyYAML** - konfigurace

---

## 📖 Dokumentace

### Pro uživatele
- **`semestral_report.md`** - Kompletní teoretický základ, implementace, experimenty
- **`METRIKY.md`** - Popis všech dostupných metrik

### Pro vývojáře
- **`experiment_examples.py`** - Praktické příklady použití
- **Komentáře v kódu** - Inline dokumentace v `sim_cafe.py`

---

## 🎓 Akademické použití

Tento projekt byl vytvořen jako semestrální práce z předmětu **Modelování a simulace (MOSIM/XMOSM)** na Ostravské univerzitě v Ostravě.

**Autor:** Michal Šeda  
**Ročník:** 2024/2025  
**Datum:** 23. ledna 2026

---

## 📄 Licence

Akademický projekt - volně použitelný pro vzdělávací účely.

---

## 🆘 FAQ

### Q: Proč je využití baristy > 100%?
**A:** Využití = průměrná fronta / kapacita × 100%. Hodnota > 100% znamená přetížení (fronty se kumulují).

### Q: Jak změním konfiguraci?
**A:** Upravte `sim_config.yaml` nebo použijte interaktivní UI s slidery.

### Q: Jak spustím více experimentů?
**A:** Viz `experiment_examples.py` - obsahuje 5 kompletních příkladů.

### Q: Kde najdu teoretický základ?
**A:** V `semestral_report.md` - kapitola 2 (Teoretický základ).

### Q: Jak přidam vlastní metriky?
**A:** Upravte metodu `get_metrics()` v třídě `StatusLog` v `sim_cafe.py`.

---

## 🚀 Další kroky

### Doporučená rozšíření:
- 📱 Online objednávky a delivery
- 💰 Ekonomické vyhodnocení (tržby vs. náklady)
- 🤖 Machine learning pro predikci příchodů
- 🔄 Adaptive staffing (dynamická úprava kapacit)
- 📊 Sledování čekacích dob (service level)

### Možné experimentální studie:
- Citlivostní analýza všech parametrů
- Multi-objective optimization (cost vs. service)
- Sezónní variace (léto vs. zima)
- Speciální události (svátky, akce)

---

**💡 Tip:** Začněte s `experiment_examples.py` a `METRIKY.md` - obsahují vše potřebné pro start!
