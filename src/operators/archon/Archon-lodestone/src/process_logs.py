import json
import csv
import os

# Update with your actual paths
LOG_PATH = "updated_gpqa_multithreaded_log.jsonl"
CONFIG_DIR = "configs/"
CSV_OUTPUT = "gpqa_wrong_multithreaded_question_cost_summary.csv"

COST_PER_1M = {
    "gpt-4o": 0.005,
    "gpt-4": 0.06,
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
        print("HI")
        if line.endswith(".json"):
            print(line, i)
            current_config = line
            config_path = os.path.join(CONFIG_DIR, current_config)
            if not os.path.isfile(config_path):
                raise FileNotFoundError(f"Config file {config_path} not found")

            layer_sequence = get_layer_type_sequence(config_path)

            # Dict to hold costs and times per question for this config
            question_data = {}

            i += 1  # Move to next line after config
            j = i   # Start a separate index for processing question data

            while j < len(lines):
                line = lines[j]

                if line.endswith(".json"):
                    break  # Next config starts, exit inner loop

                if line.startswith("Question Number"):
                    question_num = int(line.split()[-1])

                    if j + 3 >= len(lines):
                        break  # Not enough lines left for a full record

                    layer_type = lines[j + 1]
                    time_taken = float(lines[j + 2])
                    usage_data = json.loads(lines[j + 3])
                    model = usage_data["model"]
                    total_tokens = usage_data["usage"]["total_tokens"]

                    cost_per_token = COST_PER_1M.get(model, 0) / 1_000_000
                    cost = total_tokens * cost_per_token

                    if question_num not in question_data:
                        question_data[question_num] = {"cost": 0, "time": 0, "layer_count": 0}

                    question_data[question_num]["cost"] += cost
                    question_data[question_num]["time"] += time_taken
                    question_data[question_num]["layer_count"] += 1

                    j += 4  # Move to the next log entry
                else:
                    j += 1

            # After processing all questions for this config
            for qnum in sorted(question_data.keys()):
                entry = question_data[qnum]

                # Validate: only include if all layers were logged
                if entry["layer_count"] == len(layer_sequence):
                    records.append({
                        "config": current_config,
                        "question_num": qnum,
                        "total_cost_usd": round(entry["cost"], 5),
                        "total_time_sec": round(entry["time"], 4)
                    })

            i = j  # Move outer loop to the line where the inner loop stopped

        else:
            i += 1  # Move to the next line if not a config line

    # Sort records by config and question number
    records.sort(key=lambda x: (x["config"], x["question_num"]))

    # Write CSV
    with open(CSV_OUTPUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["config", "question_num", "total_cost_usd", "total_time_sec"])
        writer.writeheader()
        for row in records:
            writer.writerow(row)

    print(f"✅ Saved summary to {CSV_OUTPUT}")

if __name__ == "__main__":
    parse_log_and_write_csv()
