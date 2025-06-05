import json
import os
from config import LOG_CONFIG_FILE, DATA_FILE

def load_json(file_path, default=None):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return default or {}

def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def load_reaction_roles():
    return load_json(DATA_FILE, {})

def save_reaction_roles(data):
    save_json(DATA_FILE, data)

def load_log_config():
    return load_json(LOG_CONFIG_FILE, {})

def save_log_config(data):
    save_json(LOG_CONFIG_FILE, data)
