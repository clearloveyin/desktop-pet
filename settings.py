import json
import os
import sys
from dataclasses import dataclass

if sys.platform == 'win32':
    SETTINGS_DIR = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), '罗小黑桌宠')
else:
    SETTINGS_DIR = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', '罗小黑桌宠')
SETTINGS_FILE = os.path.join(SETTINGS_DIR, 'settings.json')


@dataclass
class Settings:
    api_endpoint: str = 'https://api.openai.com/v1'
    api_key: str = ''
    model: str = 'gpt-4o-mini'

    @classmethod
    def load(cls) -> 'Settings':
        if not os.path.exists(SETTINGS_FILE):
            return cls()
        with open(SETTINGS_FILE) as f:
            data = json.load(f)
        return cls(**{k: data.get(k, v) for k, v in cls.__dataclass_fields__.items()})

    def save(self):
        os.makedirs(SETTINGS_DIR, exist_ok=True)
        with open(SETTINGS_FILE, 'w') as f:
            json.dump({
                'api_endpoint': self.api_endpoint,
                'api_key': self.api_key,
                'model': self.model,
            }, f, indent=2)
