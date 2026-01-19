# Python + SimPy - RYCHLÝ START 🐍

## ⚡ 3 ZPŮSOBY JAK ZAČÍT

### 🥇 Nejrychlejší: Python skript (5 minut)
```bash
pip install simpy matplotlib numpy
python american_cafe_simple.py
```
**✅ Nejjednodušší - žádný Jupyter!**

### 🥈 Nejlepší: Jupyter notebook (15 minut)
```bash
pip install jupyter simpy matplotlib pandas numpy
jupyter notebook
# Otevřete american_cafe_simpy.ipynb
```
**✅ Interaktivní + krásné grafy!**

### 🥉 Pro zkušené: Vlastní skript
- Použijte kód z notebooku
- Upravte podle potřeby
- **✅ Maximální flexibilita!**

---

## 🚀 INSTALACE (Krok za krokem)

### Krok 1: Máte Python?

**Zkontrolujte:**
```bash
python --version
```

**Pokud ne:**
- Windows: https://www.python.org/downloads/ → Stáhněte Python 3.9+
- Mac: `brew install python3`
- Linux: `sudo apt install python3 python3-pip`

### Krok 2: Instalace knihoven

**Varianta A - Pouze skript:**
```bash
pip install simpy matplotlib numpy
```

**Varianta B - S Jupyter (doporučuji):**
```bash
pip install jupyter simpy matplotlib pandas numpy seaborn
```

**Kontrola instalace:**
```bash
python -c "import simpy; print('SimPy OK!')"
```

---

## 📝 METODA 1: Python skript (NEJJEDNODUŠŠÍ)

### Spuštění:

```bash
python american_cafe_simple.py
```

### Co uvidíte:

```
==================================================
🚀 AMERICKÁ KAVÁRNA - SIMULACE
==================================================

Parametry:
  Příchody: 15 zákazníků/hodinu
  Pokladny: 1
  Baristé: 2
  Stolky: 12
  Doba simulace: 300 minut (5.0 hodin)

==================================================

[simulace běží...]

==================================================
📊 VÝSLEDKY SIMULACE
==================================================

📈 ZÁKAZNÍCI:
   Celkem příchodů: 75
   Obslouženo: 75

⏱️  PRŮMĚRNÉ ČASY:
   Čekání u pokladny: 1.23 min
   Čekání na nápoj: 2.45 min
   Celkem v systému: 28.67 min

📊 FRONTY (průměr):
   U pokladny: 0.52 zákazníků
   U baru: 1.23 objednávek

==================================================

📊 Grafy uloženy do 'american_cafe_results.png'
```

### Úprava parametrů:

Otevřete `american_cafe_simple.py` v editoru a změňte:

```python
# ŘÁDKY 14-34 - ZMĚŇTE TADY:

ARRIVAL_RATE = 15        # ← ZMĚŇTE na 20 pro špičku
NUM_CASHIERS = 1         
NUM_BARISTAS = 2         # ← ZMĚŇTE na 3 pro více baristů
NUM_TABLES = 12          

SIM_TIME = 300           # ← ZMĚŇTE na 600 pro delší simulaci

VERBOSE = False          # ← ZMĚŇTE na True pro detaily
```

Pak znovu spusťte: `python american_cafe_simple.py`

---

## 📘 METODA 2: Jupyter notebook (NEJLEPŠÍ)

### Krok 1: Spusťte Jupyter

```bash
jupyter notebook
```

→ Otevře se prohlížeč automaticky!

### Krok 2: Otevřete notebook

1. Navigujte do složky se souborem
2. Klikněte na **american_cafe_simpy.ipynb**
3. Notebook se otevře!

### Krok 3: Spusťte buňky

```
Shift + Enter = Spustit buňku a přejít na další
```

**Postup:**
1. **Buňka 2** - Import knihoven (Shift+Enter)
2. **Buňka 3** - Parametry (ZMĚŇTE HODNOTY, pak Shift+Enter)
3. **Buňky 4-7** - Definice (Shift+Enter každou)
4. **Buňka 8** - SPUŠTĚNÍ SIMULACE (Shift+Enter)
5. **Buňka 9** - GRAFY (Shift+Enter)

**Uvidíte krásné grafy přímo v notebooku!** 📊

### Změna parametrů:

V **buňce 3** změňte:

```python
ARRIVAL_RATE = 15        # ← ZMĚŇTE
NUM_BARISTAS = 2         # ← ZMĚŇTE
```

Pak:
1. Shift+Enter (buňka 3)
2. Shift+Enter (buňka 8)
3. Shift+Enter (buňka 9)

**Nové výsledky okamžitě!**

---

## 🎯 POROVNÁNÍ METOD

| Vlastnost | Python skript | Jupyter notebook |
|-----------|---------------|------------------|
| **Instalace** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Jednoduchost** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Grafy** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Interaktivita** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Pro prezentaci** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Doporučení:**
- **Učíte se?** → Jupyter notebook
- **Rychle potřebujete výsledek?** → Python skript
- **Prezentace pro školu?** → Jupyter notebook

---

## 🧪 EXPERIMENTY

### Experiment 1: Vliv počtu baristů

**Python skript:**
```python
# Upravte american_cafe_simple.py:
NUM_BARISTAS = 1  # zkuste 1, 2, 3
```

**Jupyter:**
```python
# Buňka 3:
NUM_BARISTAS = 1  # zkuste 1, 2, 3
# Spusťte buňky 3, 8, 9
```

**Co sledovat:**
- Čekání na nápoj ↓ s více baristy
- Fronta u baru ↓ s více baristy

### Experiment 2: Špička vs. Klid

```python
# KLID (ráno, 7-9):
ARRIVAL_RATE = 8
SIM_TIME = 120  # 2 hodiny

# ŠPIČKA (poledne, 12-13):
ARRIVAL_RATE = 25
SIM_TIME = 60  # 1 hodina
```

### Experiment 3: Automatické porovnání

**V Jupyter notebooku (buňka 11):**

Už je tam hotový kód, který automaticky porovná 1, 2, 3 baristy!

---

## 📊 CO DOSTANETE

### 1. Textový výstup

```
⏰   0.00 min | Zákazník_1 přichází
⏰   2.15 min | Zákazník_1 u pokladny (čekal 0.00 min)
☕   4.20 min | Zákazník_1 objednal espresso
✅   5.70 min | Zákazník_1 - nápoj připraven
🪑   5.70 min | Zákazník_1 sedí u stolu
```

### 2. Statistiky

```
📊 VÝSLEDKY SIMULACE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 ZÁKAZNÍCI: 75 obslouženo
⏱️  PRŮMĚRNÉ ČASY:
   Čekání u pokladny: 1.23 min
   Celkem v systému: 28.67 min
😊 SPOKOJENOST: 100.0%
```

### 3. Grafy (4 různé)

1. **Vývoj front v čase** - čárový graf
2. **Histogram časů čekání** 
3. **Celková doba v kavárně**
4. **Sloupcový graf průměrů**

### 4. Export

**Python skript:**
- Automaticky uloží: `american_cafe_results.png`

**Jupyter:**
- Grafy přímo v notebooku
- Navíc: export do CSV možný

---

## 💡 TIPY PRO ÚSPĚCH

### Pro Python skript:

1. **Změňte `VERBOSE = True`** pro detailní výpis
2. **Upravte parametry nahoře** v souboru
3. **Spusťte vícekrát** - výsledky se liší (náhoda!)
4. **Porovnejte grafy** - uloží se vždy nový

### Pro Jupyter:

1. **Spouštějte buňky postupně** (Shift+Enter)
2. **Experimentujte v buňce 3** - změňte a znovu spusťte
3. **Použijte buňku 11** - automatické experimenty
4. **Vytvořte vlastní buňky** - můžete přidat cokoliv!

### Obecné:

1. **Spusťte simulaci vícekrát** - výsledky kolísají
2. **Porovnejte různé konfigurace**
3. **Sledujte trendy, ne jednotlivá čísla**
4. **Použijte delší `SIM_TIME`** pro stabilnější výsledky

---

## 🐛 ŘEŠENÍ PROBLÉMŮ

### "pip: command not found"

```bash
# Windows:
python -m pip install simpy

# Mac/Linux:
python3 -m pip install simpy
```

### "ModuleNotFoundError: No module named 'simpy'"

```bash
pip install simpy matplotlib numpy
```

Nebo:
```bash
pip3 install simpy matplotlib numpy
```

### "Jupyter notebook not found"

```bash
pip install jupyter notebook
```

### Grafy se nezobrazují (Jupyter)

V buňce 2 přidejte:
```python
%matplotlib inline
```

### Simulace běží moc dlouho

- Zkontrolujte `SIM_TIME` - snižte na 60-120
- Zkontrolujte `ARRIVAL_RATE` - není příliš vysoká?

---

## 📚 CO DÁL?

### 1. Porovnejte s NetLogo
- Spusťte stejné parametry
- Porovnejte výsledky
- Diskutujte rozdíly

### 2. Přidejte vlastní features
- Jídlo (delší příprava)
- Různé ceny
- Trpělivost zákazníků
- Tržby

### 3. Vytvořte český model
- Číšníci místo pokladny
- Opakované objednávky
- Prioritizace úkolů

### 4. Použijte pro úkol
- Screenshoty grafů
- Tabulky výsledků
- Porovnání konfigurací

---

## ✅ KONTROLNÍ SEZNAM

První spuštění:

- [ ] Nainstaloval jsem Python
- [ ] Nainstaloval jsem: `pip install simpy matplotlib numpy`
- [ ] Stáhl jsem `american_cafe_simple.py`
- [ ] Spustil jsem: `python american_cafe_simple.py`
- [ ] Vidím výsledky v konzoli
- [ ] Vidím soubor `american_cafe_results.png`

Nebo s Jupyter:

- [ ] Nainstaloval jsem: `pip install jupyter simpy matplotlib pandas`
- [ ] Spustil jsem: `jupyter notebook`
- [ ] Otevřel jsem `american_cafe_simpy.ipynb`
- [ ] Spustil jsem buňky 2-9
- [ ] Vidím grafy v notebooku

Experimentování:

- [ ] Změnil jsem `NUM_BARISTAS`
- [ ] Znovu spustil simulaci
- [ ] Porovnal jsem výsledky
- [ ] Zkusil jsem různé `ARRIVAL_RATE`

---

## 🎓 SHRNUTÍ

**Python + SimPy je skvělá volba protože:**

✅ Čitelný kód - skoro jako angličtina  
✅ Krásné grafy - automaticky  
✅ Flexibilní - změníte cokoliv  
✅ Profesionální - výstupy pro prezentaci  
✅ Intuitivní - pochopíte za 15 minut  

**Oproti NetLogo:**
- Méně vizuální (ne animace agentů)
- Ale MNOHEM čitelnější kód
- A lepší grafy!

---

## 📞 POTŘEBUJETE POMOC?

### Časté dotazy:

**Q: Preferuji skript nebo Jupyter?**  
A: Jupyter - kvůli interaktivitě a grafům

**Q: Musím umět Python?**  
A: Základy stačí - kód je velmi čitelný

**Q: Můžu to použít pro školu?**  
A: Ano! Je to plně funkční simulace

**Q: Jak udělám screenshot grafů?**  
A: Python skript = automaticky uloží PNG  
   Jupyter = pravý klik na graf → Save Image

---

## 🎉 ZAČNĚTE TEĎ!

**Nejrychlejší cesta:**

```bash
# 1. Instalace
pip install simpy matplotlib numpy

# 2. Stažení skriptu
# (máte american_cafe_simple.py)

# 3. Spuštění
python american_cafe_simple.py

# 4. Hotovo!
```

**Za 5 minut máte výsledky!** 🚀

---

**Hodně štěstí! Python + SimPy je opravdu lepší volba než NetLogo!** 🐍✨
