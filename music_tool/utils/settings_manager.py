import os
import json


class SettingsManager:
    def __init__(self):
        self.app_dir = os.path.join(
            os.path.expanduser("~"),
            ".pulselab_tuner"
        )

        self.settings_path = os.path.join(
            self.app_dir,
            "settings.json"
        )

        if not os.path.exists(self.app_dir):
            os.makedirs(self.app_dir)

        self.settings = {}

        self.load()

    # -------------------------

    def load(self):
        if os.path.exists(self.settings_path):
            with open(self.settings_path, "r") as f:
                self.settings = json.load(f)
        else:
            self.settings = {}

    # -------------------------

    def save(self):
        with open(self.settings_path, "w") as f:
            json.dump(self.settings, f, indent=4)

    # -------------------------

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value