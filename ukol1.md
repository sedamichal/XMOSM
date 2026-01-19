# Korespondenční úkol - Modelování a simulace
## Konceptuální modely statického a dynamického systému

---

## 1. STATICKÝ SYSTÉM: KNIHOVNA

### 1.1 Popis systému
Knihovna jako statický systém se zaměřuje na organizaci - taxonomii a umístění knih v prostoru - logistiku.
Bez časového vývoje (výpůjčky, pohyb lidí), pouze struktura a vztahy.

### 1.2 Blokové schéma struktury

```
┌──────────────────────────────────────────────────┐
│                    KNIHOVNA                      │
│  ┌────────────────────────────────────────────┐  │
│  │              KATALOGIZAČNÍ SYSTÉM          │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │  │
│  │  │ Databáze │  │  Klíče   │  │ Indexy   │  │  │
│  │  │  knih    │─→│ (ISBN,   │─→│ (autor,  │  │  │
│  │  │          │  │  název)  │  │  téma)   │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  │  │
│  └────────────────────────────────────────────┘  │
│                         │                        │
│                         ↓ mapování               │
│  ┌────────────────────────────────────────────┐  │
│  │           FYZICKÁ ORGANIZACE               │  │
│  │                                            │  │
│  │  Sekce A        Sekce B        Sekce C     │  │
│  │  ┌────────┐     ┌────────┐     ┌────────┐  │  │
│  │  │ Regál  │     │ Regál  │     │ Regál  │  │  │
│  │  │  A1    │     │  B1    │     │  C1    │  │  │
│  │  ├────────┤     ├────────┤     ├────────┤  │  │
│  │  │Police 1│     │Police 1│     │Police 1│  │  │
│  │  │Police 2│     │Police 2│     │Police 2│  │  │
│  │  │Police 3│     │Police 3│     │Police 3│  │  │
│  │  └────────┘     └────────┘     └────────┘  │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

### 1.3 Prvky systému

| Prvek | Atributy | Popis |
|-------|----------|-------|
| **Kniha** | ISBN, název, autor, rok, téma, stav, umístění | Základní prvek systému |
| **Police** | číslo, kapacita, výška, obsazenost | Fyzická jednotka úložiště |
| **Regál** | ID, sekce, počet_polic, typ (volný přístup/sklad) | Skupina polic |
| **Sekce** | název, téma, místnost | Tematická oblast |
| **Katalogový záznam** | ID_knihy, signatura, klíčová_slova | Informační prvek |

### 1.4 Vazby mezi prvky

```
Kniha ──(1:1)──→ Katalogový_záznam
  │
  └──(N:1)──→ Police ──(N:1)──→ Regál ──(N:1)──→ Sekce

Signatura:
  [SEKCE].[REGÁL].[POLICE].[POZICE]
  Příklad: "C.01.03.12" = Sekce C, Regál 01, Police 03, Pozice 12
```

### 1.5 Pravidla a omezení (statická)

1. **Kapacitní omezení**: `Σ(šířka_knih_na_polici) ≤ délka_police`
2. **Tematická konzistence**: Knihy na jednom regálu by měly patřit do stejné sekce
3. **Uspořádání**: Knihy na polici jsou řazeny podle signatury (zleva doprava)
4. **Unikátnost**: Každá kniha má jedinečnou signaturu
5. **Hierarchie**: Sekce → Regál → Police → Pozice (stromová struktura)

### 1.6 Příklad konkrétních dat

```
Sekce B: Přírodní vědy
├── Regál B1: Fyzika
│   ├── Police 1: Mechanika (15 knih)
│   ├── Police 2: Termodynamika (12 knih)
│   └── Police 3: Kvantová fyzika (8 knih)
└── Regál B2: Chemie
    ├── Police 1: Anorganická chemie (18 knih)
    └── Police 2: Organická chemie (14 knih)
```

---

## 2. DYNAMICKÝ SYSTÉM: KAVÁRNA

### 2.1 Americká kavárna (Starbucs, CostaCofee)

#### 2.1.1 Popis systému
Kavárna jako dynamický systém, kde sledujeme pohyb zákazníků, přípravu objednávek a obsluhu stolů v čase.

#### 2.1.2 Blokové schéma toku

```
┌────────────────────────────────────────────────────────────┐
│                       KAVÁRNA SYSTÉM                       │
│                                                            │
│  VSTUP           FRONTY               OBSLUHA     VÝSTUP   │
│    │                                                 │     │
│    ▼                                                 │     │
│ ┌────────┐    ┌──────────┐         ┌─────────-─┐     │     │
│ │Příchod │───→│  Fronta  │────────→│ Pokladna  │     │     │
│ │zákazn. │    │u pokladny│         │(1 obsluha)|     │     │
│ └────────┘    └──────────┘         └────-─┬────┘     │     │
│                                           │          │     │
│                                           ▼          │     │
│               ┌──────────┐         ┌──────────┐      │     │
│               │  Fronta  │←────────│Objednávka│      │     │
│               │   na     │         │ předána  │      │     │
│               │  výdej   │         └──────────┘      │     │
│               └─────┬────┘                           │     │
│                     │                                │     │
│                     ▼                                │     │
│               ┌──────────┐                           │     │
│               │ Barista  │                           │     │
│               │(2 prac.) │                           │     │
│               └─────┬────┘                           │     │
│                     │                                │     │
│                     ▼                                │     │
│               ┌───────────┐        ┌──────────┐      │     │
│               │ Výdej     │───────→│ Zákazník │──────┼────→│
│               │ objednávky│        │ odchází  │      │     │
│               └───────────┘        └──────────┘      ▼     │
│                     ▲                                      │
│                     │                           ┌────────┐ |
│    PARALELNĚ:       │                           │ Odchod │ |
│    ┌──────────┐     │                           └────────┘ |
│    │  Stolky  │─────┘                                      │
│    │(20 míst) │  zákazník sedí a konzumuje                 │
│    └──────────┘                                            │
└────────────────────────────────────────────────────────────┘
```

#### 2.1.3 Prvky systému

| Prvek | Atributy | Typ |
|-------|----------|-----|
| **Zákazník** | ID, čas_příchodu, typ_objednávky, trpělivost, stav | Dynamický agent |
| **Pokladna** | stav (volná/obsazená), aktuální_zákazník | Obsluhovací místo |
| **Barista** | ID, stav, rychlost, aktuální_úkol | Zdroj (2 instance) |
| **Fronta_pokladna** | délka, max_kapacita, FIFO_seznam | Fronta |
| **Fronta_výdeje** | seznam_objednávek, priorita | Fronta |
| **Stolek** | ID, obsazenost, kapacita | Statický zdroj |
| **Objednávka** | ID, typ_nápoje, čas_vytvoření, čas_dokončení | Úkol |

#### 2.1.4 Stavy a přechody zákazníka

```
  ┌──────────┐
  │ Příchod  │
  └────┬─────┘
       │
       ▼
┌──────────────┐
│  Čekání      │
│  u pokladny  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Objednávání  │
│ u pokladny   │
└──────┬───────┘
       │
       ├─────────→ (k odnášení)
       │               │
       ▼               │
┌──────────────┐       │
│ Čekání na    │       │
│ přípravu     │       │
└──────┬───────┘       │
       │               │
       ▼               ▼
┌──────────────┐  ┌──────────────┐
│ Hledání      │  │ Vyzvednutí   │
│ stolku       │  │ objednávky   │
└──────┬───────┘  └──────┬───────┘
       │                 │
       ▼                 │
┌──────────────┐         │
│ Konzumace    │         │
│ u stolu      │         │
└──────┬───────┘         │
       │                 │
       └────────┬────────┘
                │
                ▼
          ┌──────────┐
          │ Odchod   │
          └──────────┘
```

#### 2.1.5 Pravidla chování systému

##### Pravidlo 1: Příchod zákazníků
```
Poissonův proces s parametrem λ = 12 zákazníků/hodinu
Interval mezi příchody: exponenciální rozdělení
Průměrný interval = 60/12 = 5 minut
```

##### Pravidlo 2: Obsluha u pokladny
```
IF fronta_pokladna.isEmpty() AND pokladna.stav == "volná" THEN
    pokladna.obsluž_dalšího()
    
Doba obsluhy: normální rozdělení N(μ=2, σ=0.5) minut
```

##### Pravidlo 3: Příprava nápoje
```
barista = najdi_volného_baristu()
IF barista != NULL AND fronta_nápoje.notEmpty() THEN
    objednávka = fronta_nápoje.vezmi_první()
    barista.připrav(objednávka)
    
Doba přípravy dle typu:
- Espresso: 1.5 min
- Cappuccino: 3 min  
- Filtrovaná káva: 4 min
- Čaj: 2 min
```

##### Pravidlo 4: Hledání stolku
```
IF zákazník.typ == "k sezení" THEN
    stolek = najdi_volný_stolek()
    IF stolek == NULL THEN
        zákazník.odejdi()  // není místo
    ELSE
        stolek.obsaď()
        zákazník.sedni(stolek)
ELSE
    zákazník.odnes_a_odejdi()
```

##### Pravidlo 5: Doba konzumace
```
Doba u stolu: normální rozdělení N(μ=25, σ=10) minut
Po konzumaci: stolek.uvolni()
```

##### Pravidlo 6: Trpělivost
```
IF čekání_ve_frontě > zákazník.trpělivost THEN
    zákazník.odejdi_nespokojen()
    
Trpělivost: rovnoměrné rozdělení U(5, 15) minut
```

##### 2.1.6 Události v systému

| Událost | Podmínka spuštění | Akce |
|---------|-------------------|------|
| **Příchod** | Čas = t_příchod | Přidej zákazníka do fronty |
| **Začátek_obsluhy** | Pokladna volná & fronta neprázdná | Začni obsluhovat |
| **Konec_obsluhy** | Čas = t_start + doba_obsluhy | Vytvoř objednávku, uvolni pokladnu |
| **Začátek_přípravy** | Barista volný & objednávka čeká | Začni připravovat |
| **Konec_přípravy** | Čas = t_start + doba_přípravy | Nápoj připraven, uvolni baristu |
| **Obsazení_stolku** | Zákazník má nápoj & stolek volný | Obsaď stolek |
| **Opuštění_stolku** | Čas = t_sezení + doba_konzumace | Uvolni stolek, odejdi |
| **Ztráta_trpělivosti** | Čas_čekání > trpělivost | Zákazník odchází |

#### 2.1.7 Metriky systému

```
1. Průměrná doba v systému: E[T_systém]
2. Průměrná délka fronty: E[L_pokladna], E[L_nápoje]
3. Využití zdrojů: ρ_pokladna, ρ_barista1, ρ_barista2
4. Procento ztracených zákazníků: P_ztráta
5. Průměrná doba čekání: E[W_pokladna], E[W_nápoj]
```

---

## 3. POROVNÁNÍ SIMULOVANÉHO A REÁLNÉHO ČASU

### 3.1 Statický systém (Knihovna)

Pro statický systém nemá tok času primární význam, ale můžeme simulovat:

**Scénář**: Přeorganizování sekce (přemístění 500 knih)

| Metrický čas | Událost | Reálný čas |
|--------------|---------|------------|
| t=0 | Začátek reorganizace | 0 min |
| t=100 | Přemístěno 50 knih | 30 min |
| t=200 | Přemístěno 150 knih | 90 min |
| t=500 | Přemístěno všech 500 knih | 4 hodiny |

**Rychlost simulace**: 
- Reálný čas: 4 hodiny = 240 minut
- Simulovaný čas: 500 kroků
- Poměr: 1 krok simulace = 0.48 reálné minuty

### 3.2 Dynamický systém (Kavárna)

**Scénář**: Simulace provozu kavárny během ranní špičky (7:00-12:00)

#### Varianta A: Pomalá simulace (detailní vizualizace)

| Simulovaný čas | Událost | Reálný čas simulace |
|----------------|---------|---------------------|
| 0:00 (7:00) | Otevření | 0 s |
| 0:05 | První zákazník | 1 s |
| 0:30 | 6 zákazníků obslouženo | 6 s |
| 1:00 | Konec první hodiny | 12 s |
| 5:00 (12:00) | Konec simulace | 60 s (1 min) |

**Rychlost**: 1 simulovaná minuta = 0.2 reálné sekundy  
**Faktor zrychlení**: 300× (5 hodin → 1 minuta)

#### Varianta B: Rychlá simulace (statistická analýza)

| Simulovaný čas | Událost | Reálný čas simulace |
|----------------|---------|---------------------|
| 0:00 (7:00) | Otevření | 0 s |
| 1:00 | První hodina | 0.2 s |
| 3:00 | Špička | 0.6 s |
| 5:00 (12:00) | Konec | 1.0 s |

**Rychlost**: 1 simulovaná minuta = 0.0033 reálné sekundy  
**Faktor zrychlení**: 18,000× (5 hodin → 1 sekunda)

### 3.3 Výpočetní požadavky

**Předpoklad**: Moderní PC (3 GHz procesor)

**Kavárna simulace - 1 časový krok (Δt = 1 sekunda)**

```
Operace za krok:
- Kontrola fronty pokladny: 10 instrukcí
- Kontrola 2 baristů: 20 instrukcí  
- Kontrola 20 stolků: 40 instrukcí
- Generování náhodných čísel: 50 instrukcí
- Logování událostí: 30 instrukcí
────────────────────────────────────────
CELKEM: ~150 instrukcí/krok

Pro 5 hodin (18,000 sekund simulovaného času):
18,000 × 150 = 2,700,000 instrukcí

Reálný čas na PC:
2,700,000 / (3 × 10^9) ≈ 0.0009 s = 0.9 ms
```

**Závěr**: Simulace je rychlejší než reálný čas i při detailním výpočtu!

---

## 4. SHRNUTÍ

### Statický systém (Knihovna)
- **Prvky**: Knihy, police, regály, sekce
- **Důraz**: Prostorové vztahy, hierarchie, kapacity
- **Čas**: Zanedbán (snapshot stavu)
- **Modelovací prostředek**: Stromová struktura + atributové tabulky

### Dynamický systém (Kavárna)  
- **Prvky**: Zákazníci (agenti), zdroje (pokladna, baristé), fronty
- **Důraz**: Časový vývoj, události, stavy, průtoky
- **Čas**: Klíčový parametr
- **Modelovací prostředek**: Stavové diagramy + fronty + pravidla chování

### Klíčové rozdíly modelování

| Aspekt | Statický systém | Dynamický systém |
|--------|-----------------|------------------|
| Čas | Nepodstatný | Klíčový parametr |
| Prvky | Neměnné pozice/vlastnosti | Měnící se stavy |
| Popis | Struktura, vazby | Procesy, události |
| Simulace | Validace omezení | Časový průběh |
| Výstup | Konsistence dat | Statistiky výkonnosti |