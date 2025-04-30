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
    "OpenAI_API": ["gpt-4o", "gpt-4"],
    #"Anthropic_API": ["claude-3-5-sonnet-20240620"],
    "Together_API": [
        #"Qwen/Qwen2-72B-Instruct",
        #"microsoft/WizardLM-2-8x22B",
        "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        "Qwen/Qwen2-72B-Instruct",
        #"Qwen/Qwen1.5-72B-Chat",
       # "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",


        "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "mistralai/Mixtral-8x22B-Instruct-v0.1",
        #"databricks/dbrx-instruct"
    ]
}
CRITIC_MODELS = {
    "OpenAI_API": ["gpt-4o", "gpt-4"],
    #"Anthropic_API": ["claude-3-5-sonnet-20240620"],
    "Together_API": [
        #"Qwen/Qwen2-72B-Instruct",
        #"microsoft/WizardLM-2-8x22B",
        #"deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        "Qwen/Qwen2-72B-Instruct",
        #"Qwen/Qwen1.5-72B-Chat",
       # "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",


        #"meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        #"meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        #"mistralai/Mixtral-8x22B-Instruct-v0.1",
        #"databricks/dbrx-instruct"
    ]
}

def make_model(model_name, model_type, role, top_k=None):
    base = {
        "type": role,
        "model": model_name,
        "model_type": model_type,
        "temperature": 0.7,
        "max_tokens": 2048,
        "samples": 1
    }
    if role == "ranker" and top_k is not None:
        base["top_k"] = top_k
    return base

def random_models(role, max_models=5, min_models = 1, top_k=None):
    if role == "critic":
        # Only allow 1 critic
        model_pool = [(name, api) for api, names in CRITIC_MODELS.items() for name in names]
        selected = random.sample(model_pool, 1)
        return [make_model(name, api, role) for name, api in selected]

    elif role == "ranker":
        # Only allow 1 ranker with optional top_k
        model_pool = [(name, api) for api, names in MODELS.items() for name in names]
        selected = random.sample(model_pool, 1)
        return [make_model(name, api, role, top_k=top_k) for name, api in selected]

    elif role == "generator":
        # Random number of generators between 2 and 5 (or max available)
        model_pool = [(name, api) for api, names in MODELS.items() for name in names]
        upper_bound = min(5, len(model_pool))
        num = random.randint(2, upper_bound)
        selected = random.sample(model_pool, num)
        return [make_model(name, api, role) for name, api in selected]

    else:
        # fuser or other roles can have 1 to max_models
        model_pool = [(name, api) for api, names in MODELS.items() for name in names]
        num = random.randint(min_models, min(max_models, len(model_pool)))
        selected = random.sample(model_pool, num)
        return [make_model(name, api, role) for name, api in selected]

def generate_config(index):
    config = {
        "name": f"archon-config-{index}",
        "layers": []
    }

    # First layer must be multiple generators
    config["layers"].append(random_models("generator", max_models=5))
    roles = ["generator"]

    # Decide which valid config type we want
    config_type = random.choice([
        "gen_rank",              # 2-layer: Generator → Ranker
        "gen_fuser",             # 2-layer: Generator → Fuser
        "gen_critic_rank",       # 3-layer: Generator → Critic → Ranker
        "gen_critic_fuser",      # 3-layer: Generator → Critic → Fuser
        "gen_fuser_rank",        # 3-layer: Generator → Fuser(s) → Ranker
        "gen_rank_fuser"         # 3-layer: Generator → Ranker (top_k=3) → Fuser
    ])

    if config_type == "gen_rank":
        ranker = random_models("ranker", max_models=1)
        for model in ranker:
            model["top_k"] = 1
        config["layers"].append(ranker)

    elif config_type == "gen_fuser":
        fuser = random_models("fuser", max_models=1)
        config["layers"].append(fuser)

    elif config_type == "gen_critic_rank":
        critic = random_models("critic", max_models=1)
        ranker = random_models("ranker", max_models=1)
        for model in ranker:
            model["top_k"] = 1
        config["layers"].extend([critic, ranker])

    elif config_type == "gen_critic_fuser":
        critic = random_models("critic", max_models=1)
        fuser = random_models("fuser", max_models=1)
        config["layers"].extend([critic, fuser])

    elif config_type == "gen_fuser_rank":
        fuser = random_models("fuser", max_models=3, min_models = 2)
        ranker = random_models("ranker", max_models=1)
        for model in ranker:
            model["top_k"] = 1
        config["layers"].extend([fuser, ranker])

    elif config_type == "gen_rank_fuser":
        ranker = random_models("ranker", max_models=1)
        for model in ranker:
            model["top_k"] = random.randint(2,4)
        fuser = random_models("fuser", max_models=1)
        config["layers"].extend([ranker, fuser])

    return config


def generate_config_old(index):
    config = {
        "name": f"archon-config-{index}",
        "layers": []
    }

    config["layers"].append(random_models("generator"))
    roles = ["generator"]

    inserted_critic = False
    inserted_ranker = False
    ranker_layer_idx = None

    num_layers = random.randint(2, 3)

    # Add up to num_layers total
    while len(config["layers"]) < num_layers:
        if not inserted_critic:
            role = random.choice(["critic", "fuser"])
            if role == "critic":
                config["layers"].append(random_models("critic"))
                roles.append("critic")
                inserted_critic = True
            else:
                config["layers"].append(random_models("fuser"))
                roles.append("fuser")
        else:
            role = random.choice(["ranker", "fuser"])
            if role == "ranker":
                config["layers"].append(random_models("ranker", max_models=1))
                roles.append("ranker")
                inserted_ranker = True
                ranker_layer_idx = len(config["layers"]) - 1
            else:
                config["layers"].append(random_models("fuser"))
                roles.append("fuser")

    # Post-fix if the last layer is critic
    if roles[-1] == "critic":
        if len(config["layers"]) < 3:
            # Safe to add a post-critic step
            post_critic_role = random.choice(["ranker", "fuser"])
            config["layers"].append(random_models(post_critic_role, max_models=1))
            roles.append(post_critic_role)
            if post_critic_role == "ranker":
                inserted_ranker = True
                ranker_layer_idx = len(config["layers"]) - 1
        else:
            # Already at 3 layers → replace critic with ranker
            config["layers"][-1] = random_models("ranker", max_models=1)
            roles[-1] = "ranker"
            inserted_ranker = True
            ranker_layer_idx = len(config["layers"]) - 1

    # Final cleanup: force top_k = 1 if ranker is last with no fuser
    if inserted_ranker and "fuser" not in roles[ranker_layer_idx + 1:]:
        for model in config["layers"][ranker_layer_idx]:
            if model["type"] == "ranker":
                model["top_k"] = 1

    return config

# Generate and print the rest of the configs (till 100)
def gen_and_save_configs(NUM_CONFIGS, CONFIG_DIR):
    for i in range(1, NUM_CONFIGS + 1):
        cfg = generate_config(i)
        path = os.path.join(CONFIG_DIR, f"archon-config-{i}.json")
        with open(path, "w") as f:
            json.dump(cfg, f, indent=2)
        print(f"✅ Saved: {path}")

gen_and_save_configs(100, "configs")
'''
configs = [generate_config(i) for i in range(5)]
for cfg in configs:
    print(json.dumps(cfg, indent=2))
    print("\n" + "="*80 + "\n")'
'''
