# Holder for the Settings class (can't be in tools due to circular import/defenition with sprint)

import json
import os
"""
Be very careful here! When tl.initialize is active, all the print/error statements from 
this file get erased. Stick to adding to _defaults only (being careful with commas!). Silence the initialize function
and run this a couple times (try to break it) before sealing it back up. If print
statements begin acting strange, this class is a likely culprit. Since it called at the top
of most files and can't access sprint, it is isolted to prevent circular imports.
"""

class Settings:
    _instance = None
    _default_dir = os.path.dirname(os.path.abspath(__file__))
    _json_path = os.path.join(_default_dir, "settings.json")
    _defaults = {
        "print_level": 3,
        "error_level": 3,
        "base_directory": _default_dir, # Directory this code is in
        "default_vsp_name" : "untitled",
        "fully_stop_on_errors": 1,
        "silence": 0
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.data = {}
        self.load()

    def load(self):
        """Load settings from file or use defaults if file is missing or corrupted"""
        if not os.path.exists(self._json_path):
            print("[Settings] Settings file not found. Creating using default settings.")
            self.reset()
        else:
            try:
                with open(self._json_path, 'r') as f:
                    self.data = json.load(f)

                # Validate keys
                for key in self._defaults:
                    if key not in self.data:
                        print(f"[Settings] Key '{key}' missing. Inserting default.")
                        self.data[key] = self._defaults[key]

                # Remove unknown keys
                for key in list(self.data.keys()):
                    if key not in self._defaults:
                        print(f"[Settings] Unknown key '{key}' found. Removing.")
                        del self.data[key]

                self.save()  # Save to clean up unknowns

            except (json.JSONDecodeError, IOError):
                print("[Settings] Corrupt settings file. Resetting to defaults.")
                self.data = self._defaults.copy()
                self.save()
    def reset(self):
        self.data = self._defaults.copy()
        self.save()
    def save(self):
        with open(self._json_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        if key in self._defaults:
            self.data[key] = value
            self.save()
        else:
            print(f"[Settings] Invalid key: '{key}'")