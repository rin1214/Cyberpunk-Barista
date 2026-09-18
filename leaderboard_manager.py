import json
import os

class LeaderboardManager:
    def __init__(self, economy_ref, filename="save_data.json"):
        self.economy = economy_ref
        # Read directly from save_data.json to capture all saved player profiles
        self.filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    def update_current_player_score(self):
        """Bridge method matching what leaderboard_screen.py expects."""
        if self.economy:
            self.economy.save_economy_data()

    def get_ranked_players(self):
        """Loads all player profiles from save_data.json and sorts them by XP descending."""
        scores = []
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    all_profiles = json.load(f)
                    for name, data in all_profiles.items():
                        scores.append({
                            "name": name,
                            "xp": data.get("xp", 0),       # Tracked XP for leaderboard
                            "level": data.get("level", 1)
                        })
            except (IOError, json.JSONDecodeError):
                pass

        # Sort all saved players by XP from highest to lowest
        scores.sort(key=lambda x: x["xp"], reverse=True)
        return scores