"""
Ukázka: Jak provádět experimenty a porovnávat metriky
=====================================================

Tento skript ukazuje, jak:
1. Spustit simulaci programově (bez UI)
2. Získat metriky z běhu
3. Provést více běhů a porovnat výsledky
4. Exportovat data pro další analýzu
"""

import pandas as pd
from sim_cafe import CafeSimulation

# =================================================================
# PŘÍKLAD 1: Jeden běh s metrikami
# =================================================================

print("="*60)
print("PŘÍKLAD 1: Jeden běh simulace")
print("="*60)

sim = CafeSimulation("sim_config.yaml")

# Spustit simulaci (bez UI)
sim.run()

# Získat metriky
metrics = sim.get_last_metrics()

print("\nZískané metriky:")
for key, value in metrics.items():
    print(f"  {key}: {value}")

# Získat časovou řadu
data = sim.get_last_data()
print(f"\nZískána časová řada: {len(data)} záznamů")


# =================================================================
# PŘÍKLAD 2: Více běhů (Monte Carlo)
# =================================================================

print("\n" + "="*60)
print("PŘÍKLAD 2: 5 opakování simulace (Monte Carlo)")
print("="*60)

results = []

for run_id in range(5):
    print(f"\nBěh {run_id + 1}/5...")
    
    sim = CafeSimulation("sim_config.yaml")
    sim.run()
    
    metrics = sim.get_last_metrics()
    metrics['run_id'] = run_id
    results.append(metrics)

# Převést na DataFrame
df_results = pd.DataFrame(results)

print("\n" + "="*60)
print("SHRNUTÍ 5 BĚHŮ:")
print("="*60)

print("\nPrůměrné hodnoty:")
print(df_results[['total_served', 'total_reneged', 'success_rate']].mean())

print("\nSměrodatné odchylky:")
print(df_results[['total_served', 'total_reneged', 'success_rate']].std())


# =================================================================
# PŘÍKLAD 3: Porovnání scénářů
# =================================================================

print("\n" + "="*60)
print("PŘÍKLAD 3: Porovnání různých konfigurací")
print("="*60)

# Tento příklad předpokládá, že máte více konfiguračních souborů:
# - sim_config.yaml (baseline)
# - sim_config_more_baristas.yaml (více baristů)
# - sim_config_more_tables.yaml (více stolů)

scenarios = {
    'Baseline': 'sim_config.yaml',
    # 'Více baristů': 'sim_config_more_baristas.yaml',
    # 'Více stolů': 'sim_config_more_tables.yaml',
}

scenario_results = []

for scenario_name, config_file in scenarios.items():
    print(f"\nScénář: {scenario_name}")
    
    try:
        sim = CafeSimulation(config_file)
        sim.run()
        
        metrics = sim.get_last_metrics()
        metrics['scenario'] = scenario_name
        scenario_results.append(metrics)
    except FileNotFoundError:
        print(f"  ⚠️  Soubor {config_file} neexistuje - přeskakuji")

if scenario_results:
    df_scenarios = pd.DataFrame(scenario_results)
    
    print("\n" + "="*60)
    print("POROVNÁNÍ SCÉNÁŘŮ:")
    print("="*60)
    
    # Zobraz klíčové metriky
    comparison = df_scenarios[['scenario', 'total_served', 'total_reneged', 
                               'success_rate', 'avg_barista_queue']]
    print(comparison.to_string(index=False))
    
    # Export do CSV
    df_scenarios.to_csv('scenario_comparison.csv', index=False)
    print("\n💾 Výsledky uloženy do: scenario_comparison.csv")


# =================================================================
# PŘÍKLAD 4: Export dat pro pokročilou analýzu
# =================================================================

print("\n" + "="*60)
print("PŘÍKLAD 4: Export časových řad")
print("="*60)

sim = CafeSimulation("sim_config.yaml")
sim.run()

# Získat kompletní časovou řadu
timeseries = sim.get_last_data()

# Export do CSV
timeseries.to_csv('simulation_timeseries.csv', index=False)
print("\n💾 Časová řada uložena do: simulation_timeseries.csv")

# Ukázka analýzy
print("\nPrvních 10 záznamů:")
print(timeseries.head(10))

print("\nStatistiky front během simulace:")
print(timeseries[['cashier_queue', 'barista_queue']].describe())


# =================================================================
# PŘÍKLAD 5: Citlivostní analýza
# =================================================================

print("\n" + "="*60)
print("PŘÍKLAD 5: Citlivostní analýza (arrival rate)")
print("="*60)

# Tento příklad ukazuje, jak testovat vliv jednoho parametru
# Poznámka: Vyžaduje ruční úpravu konfigurace mezi běhy

arrival_rates = [0.8, 0.9, 1.0, 1.1, 1.2]  # Násobky baseline
sensitivity_results = []

for multiplier in arrival_rates:
    print(f"\nArrival rate: {multiplier:.1f}x baseline")
    
    # Zde by bylo potřeba upravit konfiguraci
    # sim._config.time_intervals[1].arrival_rate.value *= multiplier
    
    # Pro tuto ukázku jen spustíme baseline
    sim = CafeSimulation("sim_config.yaml")
    sim.run()
    
    metrics = sim.get_last_metrics()
    metrics['arrival_multiplier'] = multiplier
    sensitivity_results.append(metrics)

df_sensitivity = pd.DataFrame(sensitivity_results)

print("\n" + "="*60)
print("CITLIVOSTNÍ ANALÝZA - VÝSLEDKY:")
print("="*60)

print(df_sensitivity[['arrival_multiplier', 'total_served', 
                      'total_reneged', 'success_rate']].to_string(index=False))


print("\n" + "="*60)
print("VŠECHNY PŘÍKLADY DOKONČENY")
print("="*60)
print("\n💡 Tip: Tyto příklady můžete upravit pro vaše vlastní experimenty!")
