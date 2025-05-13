import os
import json

CONFIG_DIR = "configs/"  # your configs folder
TARGET_MODELS = {"gpt-4", "gpt-4o"}

def find_configs_with_gpt4_critic():
    matching_configs = []

    for filename in os.listdir(CONFIG_DIR):
        if filename.endswith(".json"):
            path = os.path.join(CONFIG_DIR, filename)

            with open(path) as f:
                config = json.load(f)

            for layer in config["layers"]:
                for model in layer:
                    if model["type"] == "critic" and model["model"] in TARGET_MODELS:
                        matching_configs.append(filename)
                        break  # No need to check further in this config

    return matching_configs

if __name__ == "__main__":
    results = find_configs_with_gpt4_critic()
    if results:
        print("✅ Configs with GPT-4 or GPT-4o as critic:")
        for cfg in results:
            print(cfg)
    else:
        print("❌ No configs found with GPT-4 or GPT-4o as critic.")
