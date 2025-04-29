import json
import csv
import os

# Update with your actual paths
LOG_PATH = "gpqa_multithreaded_log.jsonl"
CONFIG_DIR = "configs/"
CSV_OUTPUT = "gpqa_multithreaded_question_cost_summary.csv"

COST_PER_1M = {
    # OpenAI
    "gpt-4o": 0.005,  # Example rate (input+output average)
    "gpt-4": 0.06,     # Typical for 8k context (adjust if using 32k or input/output breakdown)

    # Together API (examples / placeholders, adjust as needed)
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B": 0.18,
    "Qwen/Qwen2-72B-Instruct": 0.90,
    "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo": 3.50,
    "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo": 0.88,
    "mistralai/Mixtral-8x22B-Instruct-v0.1": 0.90,
}

def get_layer_type_sequence(config_path):
    with open(config_path) as f:
        config = json.load(f)
    return [layer["type"] for group in config["layers"] for layer in group]

def parse_log_and_write_csv():
    with open(LOG_PATH) as f:
        lines = [line.strip() for line in f if line.strip()]

    current_config = None
    layer_sequence = []
    idx = 0
    records = []

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.endswith(".json"):
            current_config = line
            config_path = os.path.join(CONFIG_DIR, current_config)
            if not os.path.isfile(config_path):
                raise FileNotFoundError(f"Config file {config_path} not found")
            layer_sequence = get_layer_type_sequence(config_path)
            idx = 0
            i += 1
            continue

        if not current_config:
            i += 1
            continue

        question_num = 1
        total_cost = 0
        total_time = 0
        layer_idx = 0

        while i < len(lines):
            layer_type = lines[i]

            if layer_type.endswith(".json"):
                break

            # Skip repeated layer type lines (sometimes present in logs)
            while i + 1 < len(lines) and lines[i + 1].replace('.', '', 1).isdigit() == False and not lines[i + 1].startswith("{"):
                i += 1

            time_line = lines[i + 1]
            usage_line = lines[i + 2]

            try:
                time_taken = float(time_line)
                usage_data = json.loads(usage_line)
                model = usage_data["model"]
                total_tokens = usage_data["usage"]["total_tokens"]
            except Exception as e:
                print(f"Skipping malformed entry: {e}")
                i += 3
                continue

            cost_per_token = COST_PER_1M.get(model, 0) / 1000000
            total_cost += total_tokens * cost_per_token
            total_time += time_taken

            layer_idx += 1
            i += 3

            # Once a full question cycle is complete (based on layer sequence), record
            if layer_idx == len(layer_sequence):
                records.append({
                    "config": current_config,
                    "question_num": question_num,
                    "total_cost_usd": round(total_cost, 5),
                    "total_time_sec": round(total_time, 4)
                })
                question_num += 1
                total_cost = 0
                total_time = 0
                layer_idx = 0

    # Write CSV
    with open(CSV_OUTPUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["config", "question_num", "total_cost_usd", "total_time_sec"])
        writer.writeheader()
        for row in records:
            writer.writerow(row)

    print(f"Saved summary to {CSV_OUTPUT}")

if __name__ == "__main__":
    parse_log_and_write_csv()
