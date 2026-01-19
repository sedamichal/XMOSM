#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AMERICKÁ KAVÁRNA - SimPy simulace (Jednoduchá verze)

Spuštění: python american_cafe_simple.py

Co dělá:
- Simuluje americkou samoobslužnou kavárnu
- Vypisuje průběh do konzole
- Vytváří grafy
- Ukládá statistiky
"""

import simpy
import random
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# ============================================================================
# PARAMETRY - ZMĚŇTE PODLE POTŘEBY
# ============================================================================

ARRIVAL_RATE = 15        # zákazníků/hodinu
NUM_CASHIERS = 1         # počet pokladen
NUM_BARISTAS = 2         # počet baristů
NUM_TABLES = 12          # počet stolků

CASHIER_TIME_MEAN = 2.0  # průměr (minuty)
CASHIER_TIME_STD = 0.5   # směrodatná odchylka

DRINK_TIMES = {
    'espresso': 1.5,
    'cappuccino': 3.0,
    'tea': 2.0
}

P_WANTS_TABLE = 0.6      # pravděpodobnost, že chce sednout

CONSUMPTION_TIME_MEAN = 25
CONSUMPTION_TIME_STD = 10

SIM_TIME = 300           # 5 hodin = 300 minut

VERBOSE = False          # True = detailní výpis, False = jen shrnutí

# ============================================================================
# GLOBÁLNÍ STATISTIKY
# ============================================================================

stats = {
    'wait_cashier': [],
    'wait_drink': [],
    'time_in_system': [],
    'total_customers': 0,
    'served_customers': 0,
    'cashier_queue': [],
    'drink_queue': [],
    'queue_times': []
}

# ============================================================================
# ZÁKAZNÍK
# ============================================================================

def customer(env, name, cashier, baristas, tables):
    """Proces zákazníka v kavárně."""
    
    arrival_time = env.now
    stats['total_customers'] += 1
    
    if VERBOSE:
        print(f"⏰ {env.now:6.2f} min | {name} přichází")
    
    # === FRONTA U POKLADNY ===
    cashier_queue_start = env.now
    with cashier.request() as req:
        yield req
        
        cashier_wait = env.now - cashier_queue_start
        stats['wait_cashier'].append(cashier_wait)
        
        if VERBOSE:
            print(f"⏰ {env.now:6.2f} min | {name} u pokladny (čekal {cashier_wait:.2f} min)")
        
        service_time = max(0.5, random.gauss(CASHIER_TIME_MEAN, CASHIER_TIME_STD))
        yield env.timeout(service_time)
    
    # Výběr nápoje
    drink_type = random.choice(list(DRINK_TIMES.keys()))
    if VERBOSE:
        print(f"☕ {env.now:6.2f} min | {name} objednal {drink_type}")
    
    # === FRONTA U BARU ===
    drink_queue_start = env.now
    with baristas.request() as req:
        yield req
        
        drink_wait = env.now - drink_queue_start
        stats['wait_drink'].append(drink_wait)
        
        if VERBOSE:
            print(f"⏰ {env.now:6.2f} min | {name} - barista začíná")
        
        prep_time = DRINK_TIMES[drink_type]
        yield env.timeout(prep_time)
        
        if VERBOSE:
            print(f"✅ {env.now:6.2f} min | {name} - nápoj připraven")
    
    # === ROZHODNUTÍ: SEDNOUT / ODNÉST ===
    wants_table = random.random() < P_WANTS_TABLE
    
    if wants_table and len(tables.users) < tables.capacity:
        table_req = tables.request()
        yield table_req
        
        if VERBOSE:
            print(f"🪑 {env.now:6.2f} min | {name} sedí u stolu")
        
        consumption_time = max(5, random.gauss(
            CONSUMPTION_TIME_MEAN, 
            CONSUMPTION_TIME_STD
        ))
        yield env.timeout(consumption_time)
        
        tables.release(table_req)
        if VERBOSE:
            print(f"👋 {env.now:6.2f} min | {name} odchází ze stolu")
    else:
        if VERBOSE:
            print(f"🚶 {env.now:6.2f} min | {name} odnáší s sebou")
    
    # Celkový čas
    total_time = env.now - arrival_time
    stats['time_in_system'].append(total_time)
    stats['served_customers'] += 1
    
    if VERBOSE:
        print(f"✨ {env.now:6.2f} min | {name} odchází (celkem {total_time:.2f} min)\n")

# ============================================================================
# GENERÁTOR PŘÍCHODŮ
# ============================================================================

def customer_generator(env, cashier, baristas, tables):
    """Generuje příchody zákazníků."""
    customer_count = 0
    
    while True:
        inter_arrival = random.expovariate(ARRIVAL_RATE / 60)
        yield env.timeout(inter_arrival)
        
        customer_count += 1
        customer_name = f"Zákazník_{customer_count}"
        
        env.process(customer(env, customer_name, cashier, baristas, tables))

# ============================================================================
# MONITOR FRONT
# ============================================================================

def queue_monitor(env, cashier, baristas):
    """Zaznamenává délky front."""
    while True:
        stats['queue_times'].append(env.now)
        stats['cashier_queue'].append(len(cashier.queue))
        stats['drink_queue'].append(len(baristas.queue))
        yield env.timeout(5)

# ============================================================================
# SPUŠTĚNÍ SIMULACE
# ============================================================================

def run_simulation():
    """Spustí simulaci."""
    
    print("\n" + "="*50)
    print("🚀 AMERICKÁ KAVÁRNA - SIMULACE")
    print("="*50)
    print(f"\nParametry:")
    print(f"  Příchody: {ARRIVAL_RATE} zákazníků/hodinu")
    print(f"  Pokladny: {NUM_CASHIERS}")
    print(f"  Baristé: {NUM_BARISTAS}")
    print(f"  Stolky: {NUM_TABLES}")
    print(f"  Doba simulace: {SIM_TIME} minut ({SIM_TIME/60:.1f} hodin)")
    print("\n" + "="*50 + "\n")
    
    # Vytvoř prostředí
    env = simpy.Environment()
    
    # Vytvoř zdroje
    cashier = simpy.Resource(env, capacity=NUM_CASHIERS)
    baristas = simpy.Resource(env, capacity=NUM_BARISTAS)
    tables = simpy.Resource(env, capacity=NUM_TABLES)
    
    # Spusť procesy
    env.process(customer_generator(env, cashier, baristas, tables))
    env.process(queue_monitor(env, cashier, baristas))
    
    # Spusť simulaci
    env.run(until=SIM_TIME)
    
    # Zobraz výsledky
    print_summary()
    plot_results()

# ============================================================================
# VÝPIS VÝSLEDKŮ
# ============================================================================

def print_summary():
    """Vytiskne shrnutí výsledků."""
    
    print("\n" + "="*50)
    print("📊 VÝSLEDKY SIMULACE")
    print("="*50)
    
    print(f"\n📈 ZÁKAZNÍCI:")
    print(f"   Celkem příchodů: {stats['total_customers']}")
    print(f"   Obslouženo: {stats['served_customers']}")
    
    if stats['served_customers'] > 0:
        print(f"\n⏱️  PRŮMĚRNÉ ČASY:")
        print(f"   Čekání u pokladny: {np.mean(stats['wait_cashier']):.2f} min")
        print(f"   Čekání na nápoj: {np.mean(stats['wait_drink']):.2f} min")
        print(f"   Celkem v systému: {np.mean(stats['time_in_system']):.2f} min")
        
        print(f"\n📊 FRONTY (průměr):")
        print(f"   U pokladny: {np.mean(stats['cashier_queue']):.2f} zákazníků")
        print(f"   U baru: {np.mean(stats['drink_queue']):.2f} objednávek")
    
    print("\n" + "="*50 + "\n")

# ============================================================================
# GRAFY
# ============================================================================

def plot_results():
    """Vytvoří grafy výsledků."""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Americká kavárna - Výsledky simulace', 
                 fontsize=16, fontweight='bold')
    
    # Graf 1: Fronty v čase
    ax1 = axes[0, 0]
    ax1.plot(stats['queue_times'], stats['cashier_queue'], 
             label='Fronta u pokladny', linewidth=2)
    ax1.plot(stats['queue_times'], stats['drink_queue'], 
             label='Fronta u baru', linewidth=2)
    ax1.set_xlabel('Čas (minuty)')
    ax1.set_ylabel('Počet čekajících')
    ax1.set_title('Vývoj front v čase')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Graf 2: Histogram čekání
    ax2 = axes[0, 1]
    ax2.hist(stats['wait_cashier'], bins=20, alpha=0.7, label='U pokladny')
    ax2.hist(stats['wait_drink'], bins=20, alpha=0.7, label='Na nápoj')
    ax2.set_xlabel('Čas čekání (minuty)')
    ax2.set_ylabel('Počet zákazníků')
    ax2.set_title('Rozdělení časů čekání')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Graf 3: Celkový čas v systému
    ax3 = axes[1, 0]
    ax3.hist(stats['time_in_system'], bins=30, alpha=0.7, edgecolor='black')
    ax3.axvline(np.mean(stats['time_in_system']), color='red', 
                linestyle='--', linewidth=2, 
                label=f'Průměr: {np.mean(stats["time_in_system"]):.1f} min')
    ax3.set_xlabel('Čas v systému (minuty)')
    ax3.set_ylabel('Počet zákazníků')
    ax3.set_title('Celková doba v kavárně')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Graf 4: Souhrnné statistiky
    ax4 = axes[1, 1]
    metrics = ['Čekání\nu pokladny', 'Čekání\nna nápoj', 'Celkem\nv systému']
    values = [
        np.mean(stats['wait_cashier']),
        np.mean(stats['wait_drink']),
        np.mean(stats['time_in_system'])
    ]
    bars = ax4.bar(metrics, values, alpha=0.7, edgecolor='black')
    ax4.set_ylabel('Čas (minuty)')
    ax4.set_title('Průměrné časy')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Hodnoty nad sloupce
    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.1f}',
                 ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('american_cafe_results.png', dpi=300, bbox_inches='tight')
    print("📊 Grafy uloženy do 'american_cafe_results.png'")
    plt.show()

# ============================================================================
# HLAVNÍ PROGRAM
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*50)
    print("AMERICKÁ KAVÁRNA - SimPy Simulace")
    print("="*50)
    
    # Spusť simulaci
    run_simulation()
    
    print("\n✅ Simulace dokončena!")
    print("\n💡 TIP: Změňte parametry na začátku souboru a spusťte znovu!")
    print("="*50 + "\n")
