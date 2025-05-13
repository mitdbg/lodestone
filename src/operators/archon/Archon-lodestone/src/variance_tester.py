import csv

def find_unsolved_questions(csv_files):
    # Dictionary to track the accuracy of each question across all configs
    question_status = {}

    # Iterate over each CSV file
    for file in csv_files:
        with open(file, mode='r') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                question_num = int(row["question_num"])  # Get question number
                accuracy = row["accuracy"]  # Get accuracy of this question

                # If this is the first time seeing the question, initialize its status
                if question_num not in question_status:
                    question_status[question_num] = {"total_configs": 0, "wrong_configs": 0}

                # Update the total number of configs and the number of wrong answers
                question_status[question_num]["total_configs"] += 1
                if accuracy != "CORRECT":
                    question_status[question_num]["wrong_configs"] += 1
    
    print(question_status)

    # Find unsolved questions
    unsolved_questions = []
    for question_num, status in question_status.items():
        if status["wrong_configs"] == status["total_configs"]:
            unsolved_questions.append(question_num)

    return unsolved_questions

import csv

# Define the paths for the three CSV files
CSV_FILES = [
    "gpqa_part1.csv",  # Replace with your actual CSV file paths
    "gpqa_part2.csv",
    "gpqa_part3.csv"
]

def get_unique_configs(csv_files):
    all_configs = set()  # Use a set to avoid duplicates

    for csv_file in csv_files:
        with open(csv_file, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                all_configs.add(row["config"])  # Assuming 'config' is the column name

    return list(all_configs)

# Get the unique configs across all three CSVs
unique_configs = get_unique_configs(CSV_FILES)

# Print the unique configs or process them further
#print("Unique Configs:")
#for config in unique_configs:
    #print(config)
print(len(unique_configs))

def get_configs_from_csv(csv_file):
    configs = set()  # Use a set to avoid duplicates
    with open(csv_file, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            configs.add(row["config"])  # Assuming 'config' is the column name
    return configs

# Get the configs from each CSV
configs_1 = get_configs_from_csv(CSV_FILES[0])
configs_2 = get_configs_from_csv(CSV_FILES[1])
configs_3 = get_configs_from_csv(CSV_FILES[2])

# Find configs that are unique to each CSV or appear in multiple CSVs
only_in_csv1 = configs_1 - configs_2 - configs_3
only_in_csv2 = configs_2 - configs_1 - configs_3
only_in_csv3 = configs_3 - configs_1 - configs_2

in_both_csv1_and_csv2 = configs_1 & configs_2
in_both_csv1_and_csv3 = configs_1 & configs_3
in_both_csv2_and_csv3 = configs_2 & configs_3

in_all_three_csvs = configs_1 & configs_2 & configs_3

# Output the results
print("Configs only in CSV 1:")
print(only_in_csv1)
print(len(only_in_csv1))

print("\nConfigs only in CSV 2:")
print(only_in_csv2)
print(len(only_in_csv2))


print("\nConfigs only in CSV 3:")
print(only_in_csv3)
print(len(only_in_csv3))


print("\nConfigs in both CSV 1 and CSV 2:")
print(in_both_csv1_and_csv2)
print(len(in_both_csv1_and_csv2))

print("\nConfigs in both CSV 1 and CSV 3:")
print(in_both_csv1_and_csv3)
print(len(in_both_csv1_and_csv3))

print("\nConfigs in both CSV 2 and CSV 3:")
print(in_both_csv2_and_csv3)
print(len(in_both_csv2_and_csv3))


print("\nConfigs in all three CSVs:")
print(in_all_three_csvs)
print(len(in_all_three_csvs))

def get_configs_with_empty_accuracy(csv_file):
    configs_with_empty_accuracy = set()
    
    with open(csv_file, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check if accuracy is empty or missing
            accuracy = row.get("accuracy", "").strip()  # Adjust the field name if it's different
            if not accuracy:  # This checks if the accuracy is empty or just whitespace
                configs_with_empty_accuracy.add(row["config"])  # Assuming 'config' is the column name
    
    return configs_with_empty_accuracy

# Collect configs with empty accuracy across the CSV files
configs_empty_accuracy_1 = get_configs_with_empty_accuracy(CSV_FILES[0])
configs_empty_accuracy_2 = get_configs_with_empty_accuracy(CSV_FILES[1])
configs_empty_accuracy_3 = get_configs_with_empty_accuracy(CSV_FILES[2])

# Output the results
print("Configs with empty accuracy in CSV 1:")
print(configs_empty_accuracy_1)

print("\nConfigs with empty accuracy in CSV 2:")
print(configs_empty_accuracy_2)

print("\nConfigs with empty accuracy in CSV 3:")
print(configs_empty_accuracy_3)

# Combine results to find unique and common configs with missing accuracy
all_empty_accuracy_configs = configs_empty_accuracy_1 | configs_empty_accuracy_2 | configs_empty_accuracy_3  # Union of all three
print("\nAll configs across the three CSVs with empty accuracy:")
print(all_empty_accuracy_configs)
'''

def main():
    # List of CSV files
    csv_files = [
        "gpqa_part1.csv",
        "gpqa_part2.csv",
        "gpqa_part3.csv"
    ]

    # Find unsolved questions
    unsolved_questions = find_unsolved_questions(csv_files)

    # Output the result
    print("Unsolved Questions (No config can solve these):")
    for question_num in unsolved_questions:
        print(f"Question Number: {question_num}")

if __name__ == "__main__":
    main()
'''