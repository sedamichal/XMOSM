# SimPy Simulace Kaváren v Jupyter Notebooku

## 🎯 CO TO JE?

Python + SimPy simulace kaváren v Jupyter notebooku - **mnohem intuitivnější než NetLogo!**

**Výhody:**
- ✅ Čitelný kód (skoro jako angličtina)
- ✅ Krásné grafy automaticky
- ✅ Export do CSV/Excel
- ✅ Flexibilní experimentování
- ✅ Profesionální výstupy

---

## 📦 CO MÁTE K DISPOZICI

### 1. **american_cafe_simpy.ipynb**
Americká samoobslužná kavárna:
- Lineární tok
- FIFO fronty
- Jednoduché rozhodování
- Plně funkční s grafy

### 2. **czech_cafe_simpy.ipynb** (připravuji)
Česká kavárna s obsluhou:
- Aktivní číšníci
- Prioritizace úkolů
- Opakované objednávky
- Složitější, ale realističtější

---

## 🚀 JAK TO SPUSTIT

### Krok 1: Instalace

**Máte Python?** Zkontrolujte:
```bash
python --version
```

**Pokud ne, nainstalujte:**
- Windows: https://www.python.org/downloads/
- Mac: `brew install python3`
- Linux: `sudo apt install python3`

### Krok 2: Instalace Jupyter

```bash
pip install jupyter notebook
```

### Krok 3: Instalace SimPy a knihoven

```bash
pip install simpy matplotlib pandas numpy
```

**Nebo všechno najednou:**
```bash
pip install jupyter simpy matplotlib pandas numpy
```

### Krok 4: Spuštění Jupyter

```bash
jupyter notebook
```

→ Otevře se v prohlížeči automaticky!

### Krok 5: Otevření notebooku

1. V prohlížeči navigujte do složky s `.ipynb` soubory
2. Klikněte na `american_cafe_simpy.ipynb`
3. Notebook se otevře!

---

## 📘 JAK POUŽÍVAT NOTEBOOK

### Základní ovládání:

```
Shift + Enter  = Spustit buňku a přejít na další
Ctrl + Enter   = Spustit buňku a zůstat na ní
A              = Přidat buňku NAD (Above)
B              = Přidat buňku POD (Below)
DD             = Smazat buňku
```

### První spuštění:

1. **Buňka 1** - Instalace (pokud nemáte knihovny)
   ```python
   !pip install simpy matplotlib pandas numpy
   ```
   Spusťte JEDNOU, pak můžete zakomentovat.

2. **Buňka 2** - Import
   ```python
   import simpy
   import matplotlib.pyplot as plt
   ...
   ```
   Toto spouštějte vždy!

3. **Buňka 3** - Parametry
   ```python
   ARRIVAL_RATE = 15  # ZMĚŇTE HODNOTY TADY!
   NUM_BARISTAS = 2
   ...
   ```
   **TOHLE ZMĚŇTE podle experimentu!**

4. **Buňky 4-7** - Definice (spusťte, neměňte)

5. **Buňka 8** - SPUŠTĚNÍ SIMULACE
   ```python
   run_simulation()
   ```
   **TOHLE SPUSTÍ CELOU SIMULACI!** 🚀

6. **Buňka 9** - Grafy
   ```python
   plt.plot(...)
   ```
   Automaticky vytvoří krásné grafy!

---

## 🎮 PRAKTICKÝ PRŮVODCE

### Experiment 1: Změnit počet baristů

```python
# V buňce 3 najděte:
NUM_BARISTAS = 2

# Změňte na:
NUM_BARISTAS = 1  # nebo 3

# Pak:
# 1. Spusťte buňku 3 (Shift+Enter)
# 2. Spusťte buňku 8 (Shift+Enter)
# 3. Spusťte buňku 9 (Shift+Enter)
```

**Uvidíte:**
- Jak se změní časy čekání
- Jak se změní délky front
- Nové grafy!

### Experiment 2: Špička vs. Klid

```python
# KLID (ráno)
ARRIVAL_RATE = 8    # 8 zákazníků/hodinu
SIM_TIME = 120      # 2 hodiny

# ŠPIČKA (poledne)
ARRIVAL_RATE = 20   # 20 zákazníků/hodinu
SIM_TIME = 60       # 1 hodina
```

### Experiment 3: Porovnání konfigurací

**Použijte buňku 11** - automaticky porovná různé počty baristů!

Nebo napište vlastní:

```python
results = []

for baristas in [1, 2, 3]:
    NUM_BARISTAS = baristas
    # ... spusť simulaci
    # ... zaznamenej výsledky
    
# Zobraz tabulku
pd.DataFrame(results)
```

---

## 📊 CO NOTEBOOK VYTVOŘÍ

### 1. Textový výstup v průběhu simulace:

```
⏰   0.00 min | Zákazník_1 přichází
⏰   2.15 min | Zákazník_1 u pokladny (čekal 0.00 min)
☕   4.20 min | Zákazník_1 objednal espresso
⏰   4.20 min | Zákazník_1 - barista začíná (čekal 0.00 min)
✅   5.70 min | Zákazník_1 - nápoj připraven
🪑   5.70 min | Zákazník_1 sedí u stolu
```

### 2. Souhrnné statistiky:

```
==================================================
VÝSLEDKY SIMULACE
==================================================

📊 ZÁKAZNÍCI:
   Celkem příchodů: 75
   Obslouženo: 75
   Odešli nespokojeni: 0

⏱️  PRŮMĚRNÉ ČASY:
   Čekání u pokladny: 1.23 min
   Čekání na nápoj: 2.45 min
   Celkem v systému: 28.67 min

😊 SPOKOJENOST: 100.0%
```

### 3. Čtyři grafy:

1. **Vývoj front v čase** - čárový graf
2. **Histogram časů čekání** - rozdělení
3. **Celková doba v kavárně** - histogram
4. **Průměrné časy** - sloupcový graf

### 4. Tabulka s daty:

```
   Čekání u pokladny  Čekání na nápoj  Celkem v systému
0            0.00             0.00              5.82
1            0.31             1.45             32.18
2            0.00             2.87             28.42
...
```

---

## 💾 EXPORT DAT

### Do CSV:

```python
# V buňce 10 odkomentujte:
df.to_csv('american_cafe_results.csv', index=False)
```

Pak můžete otevřít v Excelu!

### Do obrázku:

```python
# V buňce 9 přidejte:
plt.savefig('grafy.png', dpi=300, bbox_inches='tight')
```

---

## 🎓 POROZUMĚNÍ KÓDU

### Jak SimPy funguje:

```python
# 1. VYTVOŘENÍ PROSTŘEDÍ
env = simpy.Environment()

# 2. VYTVOŘENÍ ZDROJŮ (kapacity)
cashier = simpy.Resource(env, capacity=1)  # 1 pokladna

# 3. PROCES ZÁKAZNÍKA
def customer(env, name, cashier):
    print(f"{name} přichází")
    
    # Čeká na volnou pokladnu
    with cashier.request() as req:
        yield req  # Zde čeká!
        
        # Teď má pokladnu
        yield env.timeout(2)  # Obsluha 2 minuty
    
    print(f"{name} odchází")

# 4. SPUŠTĚNÍ
env.process(customer(env, "Jan", cashier))
env.run()
```

**Klíčové koncepty:**

- `yield` = "čekej zde"
- `env.timeout(X)` = "počkej X minut"
- `with resource.request()` = "vezmi zdroj (a vrať ho pak)"

### Poissonův proces (příchody):

```python
# Exponenciální rozdělení
inter_arrival = random.expovariate(rate)
yield env.timeout(inter_arrival)
```

= Příchody jsou náhodné, ale v průměru `rate` za hodinu

### Normální rozdělení (časy obsluhy):

```python
service_time = random.gauss(mean, std)
```

= Většina okolo průměru, občas delší/kratší

---

## 🐛 ŘEŠENÍ PROBLÉMŮ

### "ModuleNotFoundError: No module named 'simpy'"

```bash
pip install simpy
```

### "Jupyter notebook not found"

```bash
pip install jupyter notebook
```

### Grafy se nezobrazují

Do buňky 2 přidejte:
```python
%matplotlib inline
```

### Simulace běží věčně

- Zkontrolujte `SIM_TIME` - není moc velké?
- Zkontrolujte `ARRIVAL_RATE` - není příliš vysoká?

### Chyba "KeyError" v grafech

- Pravděpodobně nebyla spuštěna simulace (buňka 8)
- Spusťte nejdřív buňku 8, pak 9

---

## 📚 DALŠÍ EXPERIMENTY

### 1. Přidat jídlo (delší příprava):

```python
# V customer() funkci:
if random.random() < 0.3:  # 30% objedná jídlo
    drink_type = 'food'
    
# Upravte DRINK_TIMES:
DRINK_TIMES = {
    'espresso': 1.5,
    'cappuccino': 3.0,
    'tea': 2.0,
    'food': 12.0  # Jídlo trvá déle!
}
```

### 2. Různé ceny:

```python
# Přidejte sledování tržeb
DRINK_PRICES = {
    'espresso': 45,
    'cappuccino': 65,
    'tea': 50
}

total_revenue = 0

# V customer():
total_revenue += DRINK_PRICES[drink_type]
```

### 3. Trpělivost zákazníků:

```python
# V customer():
PATIENCE = 10  # minut

# Při čekání:
cashier_queue_start = env.now
with cashier.request() as req:
    result = yield req | env.timeout(PATIENCE)
    
    if req not in result:
        # Odešel netrpělivě!
        print(f"{name} odešel - příliš dlouhá fronta")
        stats.left_unsatisfied += 1
        return
```

---

## 🎯 SHRNUTÍ VÝHOD

### SimPy vs. NetLogo:

| Vlastnost | SimPy | NetLogo |
|-----------|-------|---------|
| **Čitelnost** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Grafy** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Flexibilita** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Export dat** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Učící křivka** | ⭐⭐⭐⭐ | ⭐⭐ |

### Pro váš úkol:

✅ **Použijte SimPy pokud:**
- Umíte základy Pythonu
- Chcete profesionální grafy
- Potřebujete analyzovat data
- Chcete flexibilitu

⚠️ **Použijte NetLogo pokud:**
- Preferujete vizuální programování
- Chcete vidět agenty pohybovat se
- Zadání explicitně vyžaduje NetLogo

---

## ✅ KONTROLNÍ SEZNAM

První spuštění:

- [ ] Nainstaloval jsem Python
- [ ] Nainstaloval jsem Jupyter: `pip install jupyter`
- [ ] Nainstaloval jsem SimPy: `pip install simpy matplotlib pandas`
- [ ] Spustil jsem Jupyter: `jupyter notebook`
- [ ] Otevřel jsem notebook
- [ ] Spustil jsem buňky 2-8
- [ ] Vidím výstupy simulace
- [ ] Vidím grafy (buňka 9)

Experimentování:

- [ ] Změnil jsem `NUM_BARISTAS` v buňce 3
- [ ] Znovu spustil buňky 3, 8, 9
- [ ] Porovnal jsem výsledky
- [ ] Vyzkoušel jsem buňku 11 (automatické experimenty)
- [ ] Exportoval jsem data do CSV

---

## 🎉 DALŠÍ KROKY

1. **Projděte americký notebook**
2. **Změňte parametry a experimentujte**
3. **Vytvořte si vlastní experimenty**
4. **Použijte pro srovnání s NetLogo modelem**

---

**Hodně štěstí! Python + SimPy je opravdu intuitivnější než NetLogo!** 🐍🚀

**Máte dotazy?** Podívejte se do komentářů v notebooku - je tam vysvětleno úplně všechno!
