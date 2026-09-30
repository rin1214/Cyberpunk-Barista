import json
import os


class LeaderboardManager:
    def __init__(self, economy_ref, filename="save_data.json"):
        self.economy = economy_ref
        self.filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), filename
        )

    def update_current_player_score(self):
        if self.economy:
            self.economy.save_economy_data()

    def get_ranked_players(self):
        players = []

        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    profiles = json.load(f)

                for name, data in profiles.items():
                    players.append({
                        "name": name,
                        "xp": data.get("xp", 0),
                        "level": data.get("level", 1),
                        "credits": data.get("credits", 0)
                    })

            except (IOError, json.JSONDecodeError):
                pass

        return sorted(
            players,
            key=lambda p: p["xp"],
            reverse=True
        )