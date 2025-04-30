import json
import re

def extract_answer_from_output(output):
    """
    Extract number from 'The answer is:' line, handling dollar signs, backslashes,
    math-mode $...$, commas, and formatting.
    """
    # This will match formats like:
    # The answer is: \$20.00$
    # The answer is: $20,000.00
    # The answer is: 20.00
    match = re.search(r"The answer is:\s*(?:\\\$|\$)?\s*([0-9,]+(?:\.[0-9]+)?)", output)
    if not match:
        # Try backup match inside LaTeX math mode e.g. The answer is: \$20.00$
        match = re.search(r"The answer is:.*?([0-9,]+(?:\.[0-9]+)?)", output)
    if match:
        raw = match.group(1).replace(",", "")
        try:
            return float(raw)
        except:
            return None
    return None



def extract_answer_from_groundtruth(answer):
    match = re.search(r"####\s*\$?\s*([0-9,]+(?:\.[0-9]+)?)", answer)
    if match:
        raw = match.group(1).replace(",", "")
        try:
            return float(raw)
        except:
            return None
    return None


def compute_accuracy(json_path):
    with open(json_path) as f:
        dataset = json.load(f)

    total = 0
    correct = 0

    for pair in dataset:
        for entry in pair:
            pred = extract_answer_from_output(entry.get("output", ""))
            gold = extract_answer_from_groundtruth(entry.get("answer", ""))
            if pred is not None and gold is not None:
                total += 1
                if abs(pred - gold) < 1e-6:  # Float-safe equality
                    correct += 1
            else:
                print("Could not extract for entry:", entry.get("question", "")[:40])

    accuracy = correct / total if total > 0 else 0
    print(f"✅ Accuracy: {accuracy:.2%} ({correct}/{total})")

# Example usage
if __name__ == "__main__":
    compute_accuracy("/Users/yashaga/lodestone/src/operators/archon/Archon-lodestone/src/outputs/gsm8k/model_answer/archon-config-2.json")
