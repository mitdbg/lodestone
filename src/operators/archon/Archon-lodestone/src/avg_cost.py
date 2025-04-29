import csv
from collections import defaultdict

csv_path = "gpqa_multithreaded_question_cost_summary.csv"

# Dictionary to accumulate total cost and count per config
costs = defaultdict(lambda: {"total_cost": 0.0, "total_time": 0.0, "count": 0})

with open(csv_path, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        config = row["config"]
        cost = float(row["total_cost_usd"])
        time = float(row["total_time_sec"])
        costs[config]["total_cost"] += cost
        costs[config]["total_time"] += time
        costs[config]["count"] += 1

# Compute average cost per config
average_cost_per_config = {
    config: {"cost": round(data["total_cost"] / data["count"], 6), "time": round(data["total_time"] / data["count"], 6)}
    for config, data in costs.items()
}

print(average_cost_per_config)
