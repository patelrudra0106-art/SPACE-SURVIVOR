import json
import os

ANALYTICS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "analytics.json")

class Analytics:
    def __init__(self):
        self.data = {
            "total_kills": 0,
            "longest_survival": 0.0,
            "ability_usage": {
                "dash": 0,
                "bomb": 0,
                "ultimate": 0
            },
            "games_played": 0
        }
        self.load()

    def load(self):
        if os.path.exists(ANALYTICS_PATH):
            try:
                with open(ANALYTICS_PATH, "r") as f:
                    saved_data = json.load(f)
                    self.data.update(saved_data)
            except Exception:
                pass

    def save(self):
        with open(ANALYTICS_PATH, "w") as f:
            json.dump(self.data, f, indent=4)

    def record_kill(self):
        self.data["total_kills"] += 1

    def record_survival_time(self, time_alive):
        if time_alive > self.data["longest_survival"]:
            self.data["longest_survival"] = time_alive

    def record_ability_use(self, ability_name):
        if ability_name in self.data["ability_usage"]:
            self.data["ability_usage"][ability_name] += 1
        else:
            self.data["ability_usage"][ability_name] = 1

    def record_game_played(self):
        self.data["games_played"] += 1
