import json
import re

LETTER_TO_INDEX = {"A": 0, "B": 1, "C": 2, "D": 3}

def normalize(s):
    return re.sub(r"[^\d\w\s.-]", "", s.strip().lower())

def load_answer_correctness(config_filename):
    path = f"outputs/gpqa_diamond/model_answer/{config_filename}.jsonl"
    
    with open(path, "r") as f:
        data = json.load(f)
    
    correctness_list = []
    for entry in data:
        output = entry["output"]
        correct_index = entry["answer"]

        match = re.search(r"The answer is:\s*(.*)", output, re.IGNORECASE)
        if not match:
            correctness_list.append(False)
            continue

        answer_text = match.group(1).strip().rstrip(".")

        # 1. Try letter matching first
        letter_match = re.match(r"([A-D])", answer_text)
        if letter_match:
            pred_index = LETTER_TO_INDEX[letter_match.group(1)]
        else:
            # 2. Normalize and compare with choices
            answer_norm = normalize(answer_text)
            pred_index = None
            for idx, choice in enumerate(entry["choices"]):
                if answer_norm in normalize(choice):
                    pred_index = idx
                    break

        correctness_list.append(pred_index == correct_index)

    return correctness_list


correct_flags = load_answer_correctness("archon-config-1")
print(correct_flags)
print(len(correct_flags))
print(f"Accuracy: {sum(correct_flags)} / {len(correct_flags)} = {sum(correct_flags) / len(correct_flags):.2%}")
