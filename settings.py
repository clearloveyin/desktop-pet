import json
import os

SETTINGS_DIR = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', '罗小黑桌宠')
SETTINGS_FILE = os.path.join(SETTINGS_DIR, 'settings.json')

DEFAULT_SETTINGS = {
    'api_endpoint': 'https://api.openai.com/v1',
    'api_key': '',
    'model': 'gpt-4o-mini',
}


def load() -> dict:
    if not os.path.exists(SETTINGS_FILE):
        return dict(DEFAULT_SETTINGS)
    with open(SETTINGS_FILE) as f:
        data = json.load(f)
    merged = dict(DEFAULT_SETTINGS)
    merged.update(data)
    return merged


def save(config: dict):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(config, f, indent=2)
