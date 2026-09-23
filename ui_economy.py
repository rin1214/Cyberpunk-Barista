import json
import os

class UIEconomy:
    SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "save_data.json")
    
    STARTING_CREDITS = 100
    STARTING_XP = 0
    STARTING_LEVEL = 1
    MAX_LEVEL = 3
    MIN_CREDITS = 0

    LOCATIONS = {
        1: "Back Alley Kiosk",
        2: "Neon Lounge",
        3: "Cyber Penthouse",
    }

    def __init__(self, screen, player_name="Player"):
        self.screen = screen
        self.player_name = str(player_name).strip() if player_name else "Player"
        if not self.player_name:
            self.player_name = "Player"

        self.credits = self.STARTING_CREDITS
        self.xp = self.STARTING_XP
        self.level = self.STARTING_LEVEL
        self.location = self.LOCATIONS[self.STARTING_LEVEL]

        self.load_economy_data()

    def add_credits(self, amount):
        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return False

        self.credits += amount
        if self.credits < self.MIN_CREDITS:
            self.credits = self.MIN_CREDITS

        self.save_economy_data()
        return True

    def get_credits(self):
        return self.credits

    def set_credits(self, amount):
        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return False

        self.credits = max(self.MIN_CREDITS, amount)
        self.save_economy_data()
        return True

    def spend_credits(self, amount):
        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return False

        if amount < 0 or self.credits < amount:
            return False

        self.credits -= amount
        self.save_economy_data()
        return True

    def apply_reward(self, reward_result):
        if reward_result is None:
            return False

        if hasattr(reward_result, "net_credits"):
            credit_change = reward_result.net_credits
        elif hasattr(reward_result, "total_credits"):
            credit_change = reward_result.total_credits
        else:
            return False

        return self.add_credits(credit_change)

    def serve_order(self, is_correct=True):
        return True

    def sync_progression(self, progression):
        if progression is None:
            return False

        try:
            self.level = int(progression.level)
        except (TypeError, ValueError):
            self.level = self.STARTING_LEVEL

        self.level = max(1, min(self.level, self.MAX_LEVEL))

        try:
            self.xp = max(0, int(progression.xp))
        except (TypeError, ValueError):
            self.xp = self.STARTING_XP

        if hasattr(progression, "get_current_location"):
            location = progression.get_current_location()
            if location in self.LOCATIONS.values():
                self.location = location
            else:
                self.location = self.LOCATIONS[self.level]
        else:
            self.location = self.LOCATIONS[self.level]

        return True

    def set_level(self, level):
        try:
            level = int(level)
        except (TypeError, ValueError):
            return False

        self.level = max(1, min(level, self.MAX_LEVEL))
        self.location = self.LOCATIONS[self.level]
        self.save_economy_data()
        return True

    def set_xp(self, xp):
        try:
            xp = int(xp)
        except (TypeError, ValueError):
            return False

        self.xp = max(0, xp)
        self.save_economy_data()
        return True

    def get_level(self):
        return self.level

    def get_xp(self):
        return self.xp

    def get_player_name(self):
        return self.player_name

    def get_location(self):
        return self.location

    def reset_economy(self):
        self.credits = self.STARTING_CREDITS
        self.xp = self.STARTING_XP
        self.level = self.STARTING_LEVEL
        self.location = self.LOCATIONS[self.STARTING_LEVEL]
        self.save_economy_data()

    def save_economy_data(self):
        all_profiles = {}
        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE, "r", encoding="utf-8") as file:
                    all_profiles = json.load(file)
                if not isinstance(all_profiles, dict):
                    all_profiles = {}
            except (IOError, json.JSONDecodeError):
                all_profiles = {}

        for name, profile in all_profiles.items():
            if not isinstance(profile, dict):
                continue
            try:
                saved_level = int(profile.get("level", 1))
            except (TypeError, ValueError):
                saved_level = 1

            saved_level = max(1, min(saved_level, self.MAX_LEVEL))
            profile["level"] = saved_level
            profile["location"] = self.LOCATIONS[saved_level]

            try:
                profile["xp"] = max(0, int(profile.get("xp", 0)))
            except (TypeError, ValueError):
                profile["xp"] = 0

            try:
                profile["credits"] = max(self.MIN_CREDITS, int(profile.get("credits", self.STARTING_CREDITS)))
            except (TypeError, ValueError):
                profile["credits"] = self.STARTING_CREDITS

        self.level = max(1, min(int(self.level), self.MAX_LEVEL))
        self.xp = max(0, int(self.xp))
        self.credits = max(self.MIN_CREDITS, int(self.credits))
        self.location = self.LOCATIONS[self.level]

        all_profiles[self.player_name] = {
            "credits": self.credits,
            "xp": self.xp,
            "level": self.level,
            "location": self.location,
        }

        try:
            with open(self.SAVE_FILE, "w", encoding="utf-8") as file:
                json.dump(all_profiles, file, indent=4)
        except IOError as e:
            print(f"[ECONOMY ERROR] Could not save economy data: {e}")

    def load_economy_data(self):
        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE, "r", encoding="utf-8") as file:
                    all_profiles = json.load(file)
                if not isinstance(all_profiles, dict):
                    all_profiles = {}

                if self.player_name in all_profiles:
                    player_data = all_profiles[self.player_name]
                    if not isinstance(player_data, dict):
                        player_data = {}

                    try:
                        self.credits = max(self.MIN_CREDITS, int(player_data.get("credits", self.STARTING_CREDITS)))
                    except (TypeError, ValueError):
                        self.credits = self.STARTING_CREDITS

                    try:
                        self.xp = max(0, int(player_data.get("xp", self.STARTING_XP)))
                    except (TypeError, ValueError):
                        self.xp = self.STARTING_XP

                    try:
                        self.level = int(player_data.get("level", self.STARTING_LEVEL))
                    except (TypeError, ValueError):
                        self.level = self.STARTING_LEVEL

                    self.level = max(1, min(self.level, self.MAX_LEVEL))
                    self.location = self.LOCATIONS[self.level]

                    self.save_economy_data()
                    return
            except (IOError, json.JSONDecodeError, TypeError, ValueError):
                pass

        self.credits = self.STARTING_CREDITS
        self.xp = self.STARTING_XP
        self.level = self.STARTING_LEVEL
        self.location = self.LOCATIONS[self.STARTING_LEVEL]
        self.save_economy_data()

    def get_level_bg_color(self):
        colors = {
            1: (15, 10, 25),
            2: (25, 10, 20),
            3: (20, 5, 30),
        }
        return colors.get(self.level, colors[3])

    def get_data(self):
        return {
            "player_name": self.player_name,
            "credits": self.credits,
            "xp": self.xp,
            "level": self.level,
            "location": self.location,
        }

    def draw(self):
        pass