import random
import json
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
# Available models
MODELS = {
    "OpenAI_API": ["gpt-4o"],
    #"Anthropic_API": ["claude-3-5-sonnet-20240620"],
    "Together_API": [
        #"Qwen/Qwen2-72B-Instruct",
        "microsoft/WizardLM-2-8x22B",
        "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        #"Qwen/Qwen1.5-72B-Chat",
        #"meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "mistralai/Mixtral-8x22B-Instruct-v0.1",
        #"databricks/dbrx-instruct"
    ]
}

def make_model(model_name, model_type, role):
    base = {
        "type": role,
        "model": model_name,
        "model_type": model_type,
        "temperature": 0.7,
        "max_tokens": 2048,
        "samples": 1
    }
    if role == "ranker":
        base["top_k"] = 5
    return base

def random_models(role, max_models=5):
    num = random.randint(1, max_models)
    all_models = [(name, api) for api, names in MODELS.items() for name in names]
    selected = random.sample(all_models, num)
    return [make_model(name, api, role) for name, api in selected]

def generate_config(i):
    config = {
        "name": f"archon-config-{i+1}",
        "layers": []
    }

    # First layer: generators only
    config["layers"].append(random_models("generator"))

    # Build up to 3 additional layers
    possible_roles = ["critic", "ranker", "fuser"]
    inserted_critic = False
    max_layers = random.randint(2, 4)

    for _ in range(1, max_layers):
        if not inserted_critic:
            role = random.choice(["critic", "fuser"])
            if role == "critic" and i != max_layers - 1:
                config["layers"].append(random_models("critic", 1))
                inserted_critic = True
            else:
                config["layers"].append(random_models("fuser"))
        else:
            role = random.choice(["ranker", "fuser"])
            if i == max_layers - 1 or role == "fuser":
                config["layers"].append(random_models("fuser"))
            else:
                config["layers"].append(random_models("ranker", 1))

    return config

# Generate and print 5 configs

configs = [generate_config(i) for i in range(1)]
for cfg in configs:
    print(json.dumps(cfg, indent=2))
    print("\n" + "="*80 + "\n")
