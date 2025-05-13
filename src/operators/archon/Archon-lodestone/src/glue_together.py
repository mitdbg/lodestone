import json
import csv
import os
import re

CONFIG_DIR = "configs/"
OUTPUT_CSV = "gpqa_part4.csv"  # Output CSV

# Function to extract the answer from the output text
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

# Function to evaluate if the answer is correct
def evaluate(entry):
    answer = extract_answer(entry["output"])

    choice_labels = ["A", "B", "C", "D"]
    correct_choice = choice_labels[entry["correct_index"]]

    if answer in choice_labels:
        return answer == correct_choice
    elif answer:
        # Compare to text of correct answer
        correct_answer = entry["Correct Answer"].strip().lower()
        return correct_answer == answer
    else:
        return False

# Main function to process the CSV and evaluate answers
def main():
    # Open input CSV
    with open("gpqa_multithreaded_question_cost_summary_part4.csv", mode='r') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    # Iterate through each row and add accuracy
    for row in rows:
        config = row["config"]

        # Check if the corresponding model answer file exists
        path = f"outputs/gpqa_diamond/model_answer/{config}l"
        if not os.path.exists(path):
            print(f"Skipping missing file: {path}")
            continue

        with open(path) as f:
            data = json.load(f)

        # Get the question number from the row
        question_num = int(row["question_num"])  # Use the question_num from CSV

        # Find the corresponding entry for the current question number
        question_entry = data[question_num - 1]  # Data is indexed from 0, so use question_num - 1

        # Evaluate and set accuracy
        if evaluate(question_entry):
            row["accuracy"] = "CORRECT"
        else:
            row["accuracy"] = "WRONG"

    # Write the updated rows with accuracy to the output CSV
    with open(OUTPUT_CSV, mode='w', newline="") as outfile:
        fieldnames = reader.fieldnames + ["accuracy"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Saved updated results to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
