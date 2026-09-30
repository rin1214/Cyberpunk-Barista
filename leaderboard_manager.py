import json
import os


class LeaderboardManager:
    def __init__(self, economy_ref, filename="save_data.json"):
        self.economy = economy_ref

        self.filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            filename
        )

    # ============================================================
    # UPDATE CURRENT PLAYER SCORE
    # ============================================================

    def update_current_player_score(self):
       
        if self.economy is None:
            return

        try:
            self.economy.save_economy_data()

        except Exception as error:
            print(
                "[LEADERBOARD] "
                f"Could not update player score: {error}"
            )

    # ============================================================
    # GET RANKED PLAYERS
    # ============================================================

    def get_ranked_players(self):
        """
        Read all saved player profiles and rank them by XP.

        Highest XP appears first.

        Each player contains:
            name
            xp
            level
            credits
        """

        players = []

        # --------------------------------------------------------
        # CHECK SAVE FILE
        # --------------------------------------------------------

        if not os.path.exists(self.filepath):
            return players

        # --------------------------------------------------------
        # LOAD SAVE DATA
        # --------------------------------------------------------

        try:

            with open(
                self.filepath,
                "r",
                encoding="utf-8"
            ) as file:

                profiles = json.load(file)

        except (
            IOError,
            json.JSONDecodeError
        ) as error:

            print(
                "[LEADERBOARD] "
                f"Could not read save data: {error}"
            )

            return players

        # --------------------------------------------------------
        # MAKE SURE DATA IS A DICTIONARY
        # --------------------------------------------------------

        if not isinstance(profiles, dict):
            return players

        # --------------------------------------------------------
        # READ PLAYER PROFILES
        # --------------------------------------------------------

        for name, data in profiles.items():

            if not isinstance(data, dict):
                continue

            try:
                xp = int(
                    data.get(
                        "xp",
                        0
                    )
                )
            except (
                TypeError,
                ValueError
            ):
                xp = 0

            try:
                level = int(
                    data.get(
                        "level",
                        1
                    )
                )
            except (
                TypeError,
                ValueError
            ):
                level = 1

            try:
                credits = int(
                    data.get(
                        "credits",
                        0
                    )
                )
            except (
                TypeError,
                ValueError
            ):
                credits = 0

            players.append(
                {
                    "name": str(name),
                    "xp": max(0, xp),
                    "level": max(1, level),
                    "credits": max(0, credits)
                }
            )

        # --------------------------------------------------------
        # SORT BY XP
        # --------------------------------------------------------

        players.sort(
            key=lambda player: player["xp"],
            reverse=True
        )

        return players