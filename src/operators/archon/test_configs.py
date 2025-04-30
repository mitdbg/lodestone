import pandas as pd
import numpy as np
import time
from archon.completions import Archon
from generate_configs import generate_config
from dotenv import load_dotenv
import os

load_dotenv()

api_keys = {
    "OPENAI_API_KEY": [
        os.getenv("OPENAI_API_KEY"),
    ],
    "TOGETHER_API_KEY": [
       os.getenv("TOGETHER_API_KEY")
    ],
}

models = []
for i in range(5):
    config = generate_config(i)
    print("Model {i}")
    print(config)
    models.append(Archon(config, api_key_data=api_keys))

#models = [Archon(print("Model {i} \n" + generate_config(i)), api_key_data=api_keys) for i in range(5)]

# Constants
choices = ["A", "B", "C", "D"]
subject = "arc_easy"
csv_path = "/Users/yashaga/lodestone/benchmarks/MMLU/data/auxiliary_train/arc_easy.csv"

def softmax(x):
    z = x - np.max(x)
    return np.exp(z) / np.sum(np.exp(z))

def format_example(df, idx, include_answer=True):
    prompt = df.iloc[idx, 0]
    for j in range(len(choices)):
        prompt += f"\n{choices[j]}. {df.iloc[idx, j+1]}"
    prompt += "\nAnswer:"
    if include_answer:
        prompt += f" {df.iloc[idx, len(choices)+1]}\n\n"
    return prompt

def gen_prompt(train_df, k):
    prompt = f"The following are multiple choice questions (with answers) about {subject}.\n\n"
    for i in range(k):
        prompt += format_example(train_df, i)
    return prompt

def evaluate_arc_easy(model, dev_df, test_df, ntrain=5):
    cors = []
    all_probs = []

    for i in range(test_df.shape[0]):
        prompt_end = format_example(test_df, i, include_answer=False)
        k = ntrain
        train_prompt = gen_prompt(dev_df, k)
        prompt = train_prompt + prompt_end

        # Wrap prompt into Archon's format
        archon_prompt = [{"role": "user", "content": prompt}]
        
        # Query model
        while True:
            try:
                response = model.generate(archon_prompt)
                print("RESPONSE IS")
                print(response)
                break
            except Exception as e:
                print("Model error:", e)
                time.sleep(1)

        # Parse logprobs
        lprobs = []
        for ans in choices:
            key = f" {ans}"
            try:
                lprobs.append(response["choices"][0]["logprobs"]["top_logprobs"][0][key])
            except KeyError:
                print(f"Warning: {ans} not in top_logprobs. Assigning -100.")
                lprobs.append(-100)

        probs = softmax(np.array(lprobs))
        pred = choices[np.argmax(lprobs)]
        label = test_df.iloc[i, len(choices) + 1]
        cors.append(pred == label)
        all_probs.append(probs)

    acc = np.mean(cors)
    print(f"Accuracy on {subject}: {acc:.3f}")
    return np.array(cors), acc, np.array(all_probs)

def main():
    df = pd.read_csv(csv_path, header=None)
    dev_df = df[:2]
    test_df = df[3:4]

    for idx, model in enumerate(models):
        print(f"--- Evaluating Model {idx} ---")
        ntrain = len(dev_df)
        _, acc, _ = evaluate_arc_easy(model, dev_df, test_df, ntrain=ntrain)

if __name__ == "__main__":
    main()
