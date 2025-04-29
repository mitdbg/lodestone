import os
import time
import subprocess
import json
import csv

CONFIG_DIR = "configs/"
BENCHMARK = "gpqa_diamond"  
OUTPUT_DIR = "outputs/gpqa_diamond/model_answer/"
CSV_OUTPUT = "gpqa_diamond_results.csv"
USAGE_LOG_PATH = "/Users/yashaga/lodestone/src/operators/archon/Archon-lodestone/src/gpqa_multithreaded_log.jsonl"

LETTER_TO_INDEX = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

def run_benchmark(config_path):
    config_name = os.path.splitext(os.path.basename(config_path))[0]
    print(f"Running config: {config_name}")

    start = time.time()

    # Run benchmark via subprocess
    cmd = [
        "python3", "-m", "archon.completions.gen_answers",
        "--benchmark", BENCHMARK,
        "--config", config_path,
        "--parallel", "16"
    ]

    result = subprocess.run(cmd)

    end = time.time()
    elapsed = end - start

    if result.returncode != 0:
        print(f"Error running {config_name}: {result.stderr}")
        return 

    # Determine output file path (uses config_name by default)
    output_file = os.path.join(OUTPUT_DIR, f"{config_name}.jsonl")
    #accuracy = compute_accuracy(output_file)

    #return config_name, accuracy, elapsed

def main():
    results = []
    print(CONFIG_DIR)
    for filename in os.listdir(CONFIG_DIR):
        print(filename)
        if filename.endswith(".json") and filename == "archon-config-1.json":
            with open(USAGE_LOG_PATH, "a") as f:
                f.write(filename + "\n")
            config_path = os.path.join(CONFIG_DIR, filename)
            run_benchmark(config_path)
            '''
            results.append({
                "config_name": config_name,
                "accuracy": round(accuracy * 100, 2) if accuracy is not None else "ERROR",
                "time_seconds": round(elapsed, 2),
                "benchmark": BENCHMARK
            })
            '''

if __name__ == "__main__":
    main()
