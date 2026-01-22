# test_functions.py
import random
from sim_configuration import ConfigurationManager


def select_interval(config, current_time):
    """Najde aktivní interval pro daný čas."""
    for interval_id, interval_node in config.time_intervals.items():
        if interval_id == "label" or str(interval_id).startswith("_"):
            continue

        start, end = interval_node.time_range.metadata["range"]
        if start <= current_time < end:
            return interval_node

    return None


def select_customer_type(interval_node):
    """Z intervalu vybere typ zákazníka podle vah."""
    mix = interval_node.customer_mix.value

    ids = [int(k) for k in mix.keys()]
    weights = [float(v) for v in mix.values()]

    return random.choices(ids, weights=weights)[0]


def sample_distribution(param_node):
    """Univerzální vzorkování z distribuce."""
    import math

    if not hasattr(param_node, "metadata"):
        return 0.0

    dist = param_node.metadata.get("dist", {})
    dist_type = dist.get("type", "lognormvariate")

    if dist_type == "lognormvariate":
        # DŮLEŽITÉ: mean a std v konfiguraci jsou POŽADOVANÁ střední hodnota a směrodatná odchylka
        # Musíme je převést na parametry mu a sigma pro random.lognormvariate()

        desired_mean = dist["mean"]["value"]
        desired_std = dist["std"]["value"]

        # Pokud std je 0 nebo velmi malé, vrať přímo mean
        if desired_std < 0.001:
            return desired_mean

        # Konverze na parametry log-normálního rozdělení
        # mu = ln(m^2 / sqrt(m^2 + s^2))
        # sigma = sqrt(ln(1 + (s/m)^2))

        variance = desired_std**2
        mean_squared = desired_mean**2

        mu = math.log(mean_squared / math.sqrt(mean_squared + variance))
        sigma = math.sqrt(math.log(1 + variance / mean_squared))

        return random.lognormvariate(mu, sigma)

    elif dist_type == "bernoulli":
        p = dist["p"]["value"]
        return 1 if random.random() < p else 0

    return 0.0


def generate_group_parameters(config, customer_type_id):
    """Vygeneruje všechny parametry pro skupinu."""
    ctype_node = config.customer_types.__dict__.get(str(customer_type_id))

    size = int(max(1, round(sample_distribution(ctype_node.group_size))))
    patience = sample_distribution(ctype_node.queue_patience)
    wants_table = bool(sample_distribution(ctype_node.wants_table))
    consumption_modifier = sample_distribution(ctype_node.consumption_speed_modifier)

    return {
        "size": size,
        "patience": patience,
        "wants_table": wants_table,
        "consumption_modifier": consumption_modifier,
    }


def bernoulli(p):
    """Bernoulliho rozdělení."""
    return random.random() < p


def select_categories(config, customer_type_id):
    """Vybere kategorie pomocí Bernoulliho s pojistkou."""
    ctype_node = config.customer_types.__dict__.get(str(customer_type_id))
    cat_weights = ctype_node.order_categories_preferences.value

    total_weight = sum(float(w) for w in cat_weights.values())

    if total_weight == 0:
        return []

    selected_categories = []

    for cat_id_str, weight in cat_weights.items():
        probability = float(weight) / total_weight

        if bernoulli(probability):
            selected_categories.append(int(cat_id_str))

    # POJISTKA
    if not selected_categories:
        max_cat_id = max(cat_weights.items(), key=lambda x: float(x[1]))[0]
        selected_categories = [int(max_cat_id)]

    return selected_categories


def select_item_from_category(config, category_id):
    """Z kategorie vybere položku podle vah."""
    cat_node = config.item_categories.__dict__.get(str(category_id))
    item_weights = cat_node.items_weights.value

    ids = [int(k) for k in item_weights.keys()]
    weights = [float(v) for v in item_weights.values()]

    return random.choices(ids, weights=weights)[0]


def create_order_for_customer(config, customer_type_id):
    """Vytvoří kompletní objednávku pro jednoho zákazníka."""
    order = []

    selected_categories = select_categories(config, customer_type_id)

    for category_id in selected_categories:
        item_id = select_item_from_category(config, category_id)
        order.append(item_id)

    return order


def get_recipe_steps(config, item_id):
    """Získá kroky receptu pro položku."""
    item_node = config.menu_items.__dict__.get(str(item_id))

    if not item_node or not hasattr(item_node, "recipe"):
        return []

    steps = []
    for step_id, step_node in item_node.recipe.items():
        if step_id == "label" or str(step_id).startswith("_"):
            continue

        resources = step_node.task_used_resources.value
        duration = sample_distribution(step_node.recipe_time)

        steps.append((int(step_id), resources, duration))

    steps.sort(key=lambda x: x[0])

    return steps
