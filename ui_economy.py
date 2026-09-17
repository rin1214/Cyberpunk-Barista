import json
import os
import pygame


class UIEconomy:

  def __init__(self, screen, player_name="Player"):
    self.screen = screen
    self.player_name = player_name

    # Economy & Level Tracking
    self.level = 1
    self.credits = 0
    self.xp = 0
    self.xp_to_next_level = 100

    # Locations corresponding to levels
    self.LOCATIONS = {
        1: "NEON ALLEY CAFE",
        2: "CYBER DOCK COFFEE",
        3: "HIGH-RISE BAR",
    }
    self.location = self.LOCATIONS[self.level]

    # Save File Path
    self.save_dir = "saves"
    self.save_file = os.path.join(
        self.save_dir, f"{self.player_name}_economy.json"
    )

    # Initialize font engine
    pygame.font.init()
    self.font_title = pygame.font.SysFont("Consolas", 20, bold=True)
    self.font_stat = pygame.font.SysFont("Consolas", 16)

    # Load existing player data if available
    self.load_economy_data()

  # --------------------------------------------------
  # ORDER HANDLING & PROGRESSION
  # --------------------------------------------------
  def serve_order(self, is_correct=True):
    """Updates credits, XP, and triggers leveling logic based on drink accuracy."""
    if is_correct:
      self.credits += 20
      self.xp += 30
      print(
        f"[ECONOMY] Correct Order! +20 Credits | +30 XP ({self.xp}/{self.xp_to_next_level})"
      )
    else:
      self.credits = max(0, self.credits - 5)
      print(f"[ECONOMY] Incorrect Order! -5 Credits Penalty")

    # Check for level up progression
    self.check_level_up()
    self.save_economy_data()

  def check_level_up(self):
    """Handles level transitions and updates locations."""
    while self.xp >= self.xp_to_next_level and self.level < 3:
      self.xp -= self.xp_to_next_level
      self.level += 1
      self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
      self.location = self.LOCATIONS.get(self.level, "UNKNOWN ZONE")
      print(
        f"[LEVEL UP] {self.player_name} reached Level {self.level}: {self.location}!"
      )

  def reset_economy(self):
    """Resets economy stats to level 1 baseline."""
    self.level = 1
    self.credits = 0
    self.xp = 0
    self.xp_to_next_level = 100
    self.location = self.LOCATIONS[1]
    self.save_economy_data()
    print(f"[ECONOMY] Profile for '{self.player_name}' reset to Level 1.")

  # --------------------------------------------------
  # DATA PERSISTENCE (SAVE / LOAD)
  # --------------------------------------------------
  def save_economy_data(self):
    """Saves player stats to a JSON file."""
    if not os.path.exists(self.save_dir):
      os.makedirs(self.save_dir)

    data = {
        "player_name": self.player_name,
        "level": self.level,
        "credits": self.credits,
        "xp": self.xp,
        "xp_to_next_level": self.xp_to_next_level,
        "location": self.location,
    }

    try:
      with open(self.save_file, "w") as f:
        json.dump(data, f, indent=4)
      print(f"[SAVE] Progress saved for '{self.player_name}'")
    except Exception as e:
      print(f"[SAVE ERROR] Could not save economy data: {e}")

  def load_economy_data(self):
    """Loads player stats from JSON if it exists."""
    if os.path.exists(self.save_file):
      try:
        with open(self.save_file, "r") as f:
          data = json.load(f)
          self.level = data.get("level", 1)
          self.credits = data.get("credits", 0)
          self.xp = data.get("xp", 0)
          self.xp_to_next_level = data.get("xp_to_next_level", 100)
          self.location = data.get(
              "location", self.LOCATIONS.get(self.level, "NEON ALLEY CAFE")
          )
        print(f"[LOAD] Loaded profile for '{self.player_name}'")
      except Exception as e:
        print(f"[LOAD ERROR] Could not read save file: {e}")

  # --------------------------------------------------
  # UI RENDERING ENGINE
  # --------------------------------------------------
  def draw(self):
    """Renders the HUD overlay on screen."""
    # HUD Container Box
    overlay = pygame.Surface((320, 100), pygame.SRCALPHA)
    overlay.fill((10, 10, 20, 200))  # Semi-transparent dark background
    self.screen.blit(overlay, (20, 20))

    # Outer Neon Border
    pygame.draw.rect(
        self.screen, (0, 255, 204), (20, 20, 320, 100), 2, border_radius=4
    )

    # Header Text
    header_str = f"BARISTA: {self.player_name.upper()}"
    surf_header = self.font_title.render(header_str, True, (0, 255, 204))
    self.screen.blit(surf_header, (30, 28))

    # Stat Texts
    location_str = f"LOC: {self.location}"
    stats_str = f"LVL: {self.level} | CREDITS: ${self.credits} | XP: {self.xp}/{self.xp_to_next_level}"

    surf_loc = self.font_stat.render(location_str, True, (255, 204, 0))
    surf_stats = self.font_stat.render(stats_str, True, (255, 255, 255))

    self.screen.blit(surf_loc, (30, 58))
    self.screen.blit(surf_stats, (30, 82))