import json
import re
import os
'''
configs = [
    "archon-config-43.json",
    "archon-config-1.json",
    "archon-config-23.json",
    "archon-config-53.json",
    "archon-config-45.json",
    "archon-config-7.json",
    "archon-config-86.json",
    "archon-config-28.json",
    "archon-config-65.json",
    "archon-config-68.json",
    "archon-config-92.json",
    "archon-config-84.json",
    "archon-config-67.json",
    "archon-config-30.json",
    "archon-config-31.json",
    "archon-config-11.json",
    "archon-config-93.json",
    "archon-config-94.json",
    "archon-config-82.json",
    "archon-config-16.json",
    "archon-config-60.json",
    "archon-config-76.json",
    "archon-config-21.json"
]

import os

directory = "outputs/gpqa_diamond/model_answer"
filenames = [f[:-1] for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

union = list(set(configs) | set(filenames))

print(union)
print(len(union))
'''
CONFIG_DIR = "configs/"
INPUT_PATH = "outputs/gpqa_diamond/model_answer/archon-config-43.jsonl"  # Replace with your actual path
OUTPUT_CSV = "test_results.csv"

def extract_answer_old(output):
    """Extract the final answer from the output text."""
    match = re.search(r"The answer is[:\s]*([A-D])(?:\.|$)", output.strip(), re.IGNORECASE)
    if match:
        return match.group(1).upper()
    else:
        # If no choice given, try to extract the text answer
        text_match = re.search(r"The answer is[:\s]*(.+)$", output.strip(), re.IGNORECASE)
        if text_match:
            return text_match.group(1).strip().lower()
        else:
            return None

def extract_answer(output):
    """Extract the final answer from the output text."""
    match = re.search(r"The answer is[:\s]*([A-D])(?:[\.\s]|$)", output.strip(), re.IGNORECASE)
    if match:
        return match.group(1).upper()
    else:
        # If no choice given, try to extract the text answer
        text_match = re.search(r"The answer is[:\s]*[A-D]?[\.]?\s*(.+)$", output.strip(), re.IGNORECASE)
        if text_match:
            return text_match.group(1).strip().lower()
        else:
            return None

def evaluate(entry):
    answer = extract_answer(entry["output"])
    #print("ANSWER IS ", answer)

    choice_labels = ["A", "B", "C", "D"]
    correct_choice = choice_labels[entry["correct_index"]]

    if answer in choice_labels:
        #print("CORRECT CHOICE IS ", correct_choice, answer == correct_choice)
        return answer == correct_choice
    elif answer:
        # Compare to text of correct answer
        correct_answer = entry["Correct Answer"].strip().lower()
        #print("CORRECT ANSWER IS ", correct_answer, correct_answer == answer)
        return correct_answer == answer
    else:
        #print("WRONG ANSWER, 0")
        return False

def main():
    # Load data
    for config in os.listdir(CONFIG_DIR):
        path = "outputs/gpqa_diamond/model_answer/" + config + "l"
        if not os.path.exists(path):
            print(f"Skipping missing file: {path}")
            continue

        with open(path) as f:
            data = json.load(f)

        print(config)
        total = len(data)
        correct = 0
        i = 1
        for entry in data:
            #print("QUESTION #", i)
            if evaluate(entry):
                correct += 1
            i += 1

        accuracy = correct / total if total > 0 else 0
        print(f"Accuracy: {accuracy:.2%} ({correct}/{total})")
        #print(data[91])

if __name__ == "__main__":
    main()
