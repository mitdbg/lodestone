import os
import time
import subprocess
import json
import csv

CONFIG_DIR = "configs/"
BENCHMARK = "gpqa_diamond"  
OUTPUT_DIR = "outputs/gpqa_diamond/model_answer/"
CSV_OUTPUT = "gpqa_diamond_results.csv"
USAGE_LOG_PATH = "/Users/yashaga/lodestone/src/operators/archon/Archon-lodestone/src/gpqa_multithreaded_log_part4.jsonl"

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
    already_processed = ['archon-config-38.json', 'archon-config-86.json', 'archon-config-44.json', 'archon-config-92.json', 'archon-config-13.json', 'archon-config-58.json', 'archon-config-15.json', 'archon-config-65.json', 'archon-config-11.json', 'archon-config-19.json', 'archon-config-76.json', 'archon-config-100.json', 'archon-config-7.json', 'archon-config-84.json', 'archon-config-5.json', 'archon-config-62.json', 'archon-config-59.json', 'archon-config-91.json', 'archon-config-39.json', 'archon-config-26.json', 'archon-config-55.json', 'archon-config-31.json', 'archon-config-51.json', 'archon-config-63.json', 'archon-config-48.json', 'archon-config-68.json', 'archon-config-35.json', 'archon-config-42.json', 'archon-config-52.json', 'archon-config-81.json', 'archon-config-22.json', 'archon-config-23.json', 'archon-config-60.json', 'archon-config-34.json', 'archon-config-97.json', 'archon-config-43.json', 'archon-config-28.json', 'archon-config-12.json', 'archon-config-67.json', 'archon-config-1.json', 'archon-config-73.json', 'archon-config-90.json', 'archon-config-32.json', 'archon-config-47.json', 'archon-config-75.json', 'archon-config-25.json', 'archon-config-94.json', 'archon-config-69.json', 'archon-config-74.json', 'archon-config-82.json', 'archon-config-30.json', 'archon-config-49.json', 'archon-config-96.json', 'archon-config-78.json', 'archon-config-16.json', 'archon-config-21.json', 'archon-config-33.json', 'archon-config-80.json', 'archon-config-87.json', 'archon-config-24.json', 'archon-config-72.json', 'archon-config-45.json', 'archon-config-53.json', 'archon-config-14.json', 'archon-config-93.json', 'archon-config-6.json', 'archon-config-18.json', 'archon-config-79.json']
    empty_accuracy = ['archon-config-54.json', 'archon-config-83.json', 'archon-config-29.json', 'archon-config-10.json', 'archon-config-64.json', 'archon-config-92.json']
    #print("LEN IS", len(already_processed))
    for filename in os.listdir(CONFIG_DIR):
        print(filename)
        if filename.endswith(".json") and filename in empty_accuracy:
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
