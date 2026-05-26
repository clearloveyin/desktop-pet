import os
import tempfile
from unittest.mock import patch


def test_load_returns_defaults_when_file_missing():
    with tempfile.TemporaryDirectory() as tmp:
        fake_file = os.path.join(tmp, 'settings.json')
        with patch('settings.SETTINGS_FILE', fake_file):
            from settings import load, DEFAULT_SETTINGS
            result = load()
            assert result == DEFAULT_SETTINGS


def test_save_and_load_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        fake_file = os.path.join(tmp, 'settings.json')
        with patch('settings.SETTINGS_FILE', fake_file):
            from settings import load, save
            config = {
                'api_endpoint': 'https://custom.com/v1',
                'api_key': 'sk-test',
                'model': 'gpt-4',
            }
            save(config)
            loaded = load()
            assert loaded == config


def test_load_merges_defaults_for_missing_keys():
    with tempfile.TemporaryDirectory() as tmp:
        fake_file = os.path.join(tmp, 'settings.json')
        with patch('settings.SETTINGS_FILE', fake_file):
            from settings import load, save, DEFAULT_SETTINGS
            save({'api_endpoint': 'http://local:8000/v1'})
            result = load()
            assert result['api_endpoint'] == 'http://local:8000/v1'
            assert result['api_key'] == DEFAULT_SETTINGS['api_key']
