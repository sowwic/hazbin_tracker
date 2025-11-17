import json
from hazbin_tracker.core.constants import CONFIG_FILE_PATH


DEFAULT_CONFIG = {
    "PUSHOVER_USER_KEY": "",
    "PUSHOVER_HAZBIN_APP_KEY": "",
    "PUSHOVER_ENABLED": 1
}


def load_keys():
    if CONFIG_FILE_PATH.exists():
        data = json.loads(CONFIG_FILE_PATH.read_text())
        return data["PUSHOVER_USER_KEY"], data["PUSHOVER_HAZBIN_APP_KEY"]
    else:
        CONFIG_FILE_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=4))
        return None, None


def load_config_file():
    return json.loads(CONFIG_FILE_PATH.read_text())
