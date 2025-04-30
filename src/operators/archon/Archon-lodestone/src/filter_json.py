import json

input_path = "/Users/yashaga/lodestone/src/operators/archon/Archon-lodestone/src/outputs/gpqa_diamond/model_answer/archon-config-1.jsonl"  # Replace with your actual file path
output_path = "filtered_gpqa_diamond.json"

# List of fields to retain
desired_fields = [
    "Question",
    "Correct Answer",
    "Incorrect Answer 1",
    "Incorrect Answer 2",
    "Incorrect Answer 3",
    "Explanation",
    "prompt",
    "output",
    "generator"
]

# Read and filter the data
with open(input_path, "r") as f:
    data = json.load(f)

filtered_data = []
for record in data:
    filtered_record = {key: record.get(key) for key in desired_fields}
    filtered_data.append(filtered_record)

# Write filtered data to a new file
with open(output_path, "w") as f:
    json.dump(filtered_data, f, indent=2)

print(f"Filtered data written to {output_path}")
