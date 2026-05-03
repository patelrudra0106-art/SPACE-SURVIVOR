import json
import os

META_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "meta_progression.json")

class MetaProgression:
    def __init__(self):
        self.data = {
            "credits": 0,
            "hp_level": 1,
            "fire_rate_level": 1,
            "unlocked_abilities": ["dash"] # Dash starts unlocked, bomb and ult locked
        }
        self.load()

    def load(self):
        if os.path.exists(META_PATH):
            try:
                with open(META_PATH, "r") as f:
                    saved_data = json.load(f)
                    self.data.update(saved_data)
            except Exception:
                pass

    def save(self):
        with open(META_PATH, "w") as f:
            json.dump(self.data, f, indent=4)

    def add_credits(self, amount):
        self.data["credits"] += amount
        self.save()

    def spend_credits(self, amount) -> bool:
        if self.data["credits"] >= amount:
            self.data["credits"] -= amount
            self.save()
            return True
        return False

    def upgrade_hp(self, cost):
        if self.spend_credits(cost):
            self.data["hp_level"] += 1
            self.save()
            return True
        return False

    def upgrade_fire_rate(self, cost):
        if self.spend_credits(cost):
            self.data["fire_rate_level"] += 1
            self.save()
            return True
        return False

    def unlock_ability(self, ability_name, cost):
        if ability_name not in self.data["unlocked_abilities"] and self.spend_credits(cost):
            self.data["unlocked_abilities"].append(ability_name)
            self.save()
            return True
        return False
