import os
import time
import subprocess
import json
import csv

# Constants
CONFIG_DIR = "configs/"
BENCHMARK = "mmlu"  
OUTPUT_DIR = "outputs/mmlu/model_answer/"
CSV_OUTPUT = "gsm8k_results.csv"
USAGE_LOG_PATH = "/Users/yashaga/lodestone/src/operators/archon/Archon-lodestone/src/token_usage_log2.jsonl"

LETTER_TO_INDEX = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

def extract_predicted_index(output):
    try:
        last_line = output.strip().splitlines()[-1]
        if "The answer is:" in last_line:
            answer_letter = last_line.split("The answer is:")[1].strip().replace('.', '')
            return LETTER_TO_INDEX.get(answer_letter)
    except Exception as e:
        print(f"Error parsing output:\n{output}\nReason: {e}")
    return None

def compute_accuracy(file_path):
    correct = 0
    total = 0

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Could not load {file_path}: {e}")
        return None

    for entry in data:
        gold = entry.get("answer")
        output = entry.get("output", "")
        pred = extract_predicted_index(output)

        if pred is not None:
            total += 1
            if pred == gold:
                correct += 1

    return correct / total if total > 0 else 0

def run_benchmark(config_path):
    config_name = os.path.splitext(os.path.basename(config_path))[0]
    print(f"Running config: {config_name}")

    start = time.time()

    # Run benchmark via subprocess
    cmd = [
        "python3", "-m", "archon.completions.gen_answers",
        "--benchmark", BENCHMARK,
        "--config", config_path,
        "--parallel", "1"
    ]

    result = subprocess.run(cmd)

    end = time.time()
    elapsed = end - start

    if result.returncode != 0:
        print(f"Error running {config_name}: {result.stderr}")
        return config_name, None, elapsed

    # Determine output file path (uses config_name by default)
    output_file = os.path.join(OUTPUT_DIR, f"{config_name}.jsonl")
    accuracy = compute_accuracy(output_file)

    return config_name, accuracy, elapsed

def main():
    results = []

    for filename in os.listdir(CONFIG_DIR):
        if filename.endswith(".json"):
            with open(USAGE_LOG_PATH, "a") as f:
                f.write(filename + "\n")
            config_path = os.path.join(CONFIG_DIR, filename)
            config_name, accuracy, elapsed = run_benchmark(config_path)
            results.append({
                "config_name": config_name,
                "accuracy": round(accuracy * 100, 2) if accuracy is not None else "ERROR",
                "time_seconds": round(elapsed, 2),
                "benchmark": BENCHMARK
            })
            #break

    # Write results to CSV
    with open(CSV_OUTPUT, "w", newline="") as csvfile:
        fieldnames = ["config_name", "accuracy", "time_seconds", "benchmark"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"Saved summary to {CSV_OUTPUT}")

if __name__ == "__main__":
    main()
    
