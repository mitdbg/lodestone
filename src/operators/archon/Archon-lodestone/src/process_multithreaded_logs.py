import json
import csv
import os

# Update with your actual paths
LOG_PATH = "gpqa_multithreaded_log_part4.jsonl"
CONFIG_DIR = "configs/"
CSV_OUTPUT = "gpqa_multithreaded_question_cost_summary_part4.csv"

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
            i += 1

            # NEW: Start collecting question data fresh for this config
            question_data = {}

            # Start processing this config’s logs until the next config or end of file
            while i < len(lines):
                line = lines[i]
                if line.endswith(".json"):
                    break  # Next config starts

                if line.startswith("Question Number"):
                    question_num = int(line.split()[-1])
                    i += 1
                    if i + 2 >= len(lines):
                        break

                    layer_type = lines[i]
                    time_taken = float(lines[i + 1])
                    usage_data = json.loads(lines[i + 2])
                    model = usage_data["model"]
                    total_tokens = usage_data["usage"]["total_tokens"]

                    cost_per_token = COST_PER_1M.get(model, 0) / 1_000_000
                    cost = total_tokens * cost_per_token

                    if question_num not in question_data:
                        question_data[question_num] = {"cost": 0, "time": 0}

                    question_data[question_num]["cost"] += cost
                    question_data[question_num]["time"] += time_taken

                    i += 3
                else:
                    i += 1

            # After processing all questions for this config, store the results
            if question_data:
                max_q = max(question_data.keys())
                for qnum in range(1, max_q + 1):
                    entry = question_data.get(qnum, {"cost": 0, "time": 0})
                    records.append({
                        "config": current_config,
                        "question_num": qnum,
                        "total_cost_usd": round(entry["cost"], 5),
                        "total_time_sec": round(entry["time"], 4)
                    })

        else:
            i += 1  # Skip lines outside of configs

    # Write CSV
    records = sorted(records, key=lambda x: (x["config"], x["question_num"]))

    with open(CSV_OUTPUT, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["config", "question_num", "total_cost_usd", "total_time_sec"]
        )
        writer.writeheader()
        for row in records:
            writer.writerow(row)

    print(f"Saved summary to {CSV_OUTPUT}")


def parse_log_and_write_csv_old():
    with open(LOG_PATH) as f:
        lines = [line.strip() for line in f if line.strip()]

    current_config = None
    layer_sequence = []
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
            i += 1
            continue

        if not current_config:
            i += 1
            continue

        # Collect all log entries by question number
        question_data = {}

        while i < len(lines):
            line = lines[i]
            if line.endswith(".json"):
                break

            if line.startswith("Question Number"):
                question_num = int(line.split()[-1])
                i += 1
                if i + 2 >= len(lines):
                    break

                layer_type = lines[i]
                time_taken = float(lines[i + 1])
                usage_data = json.loads(lines[i + 2])
                model = usage_data["model"]
                total_tokens = usage_data["usage"]["total_tokens"]

                cost_per_token = COST_PER_1M.get(model, 0) / 1_000_000
                cost = total_tokens * cost_per_token

                if question_num not in question_data:
                    question_data[question_num] = {"cost": 0, "time": 0}

                question_data[question_num]["cost"] += cost
                question_data[question_num]["time"] += time_taken

                i += 3
            else:
                i += 1

        # After parsing all question data for this config, write records
        max_q = max(question_data.keys())
        for qnum in range(1, max_q + 1):
            entry = question_data.get(qnum, {"cost": 0, "time": 0})
            records.append({
                "config": current_config,
                "question_num": qnum,
                "total_cost_usd": round(entry["cost"], 5),
                "total_time_sec": round(entry["time"], 4)
            })

    # Write CSV in order of question number
    records = sorted(records, key=lambda x: (x["config"], x["question_num"]))

    with open(CSV_OUTPUT, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["config", "question_num", "total_cost_usd", "total_time_sec"]
        )
        writer.writeheader()
        for row in records:
            writer.writerow(row)

    print(f"Saved summary to {CSV_OUTPUT}")

if __name__ == "__main__":
    parse_log_and_write_csv()