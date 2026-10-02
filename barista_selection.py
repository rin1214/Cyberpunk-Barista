from __future__ import annotations

import json
import os
import pygame

BARISTA_DATA = {
    "Ryu": {
        "cost": 0,
        "color": (75, 225, 255),
        "role": "ROOKIE BARISTA",
        "ability": "BALANCED",
        "description": "No special bonus,\nbut reliable in all situations.",
        "avatar": "ryu.png",
    },
    "Kira": {
        "cost": 1000,
        "color": (255, 80, 190),
        "role": "SPEEDSTER",
        "ability": "QUICK HANDS",
        "description": "Preparation time is\n20% faster for all drinks.",
        "avatar": "kira.png",
    },
    "Jax": {
        "cost": 2000,
        "color": (90, 235, 165),
        "role": "MONEY MAKER",
        "ability": "EXTRA INCOME",
        "description": "Earn 20% more credits\nfrom every customer.",
        "avatar": "jax.png",
    },
}

BARISTAS = ("Ryu", "Kira", "Jax")
SAVE_FILE = "barista_unlocks.json"
BACKGROUND_FILE = "barista_selection_bg.jpg"


class BaristaSelection:
    """Barista selection with a separate confirmation step and per-player unlocks."""

    WIDTH = 1280
    HEIGHT = 720

    def __init__(self, screen, economy=None):
        self.screen = screen
        self.economy = economy
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.save_path = os.path.join(self.project_root, SAVE_FILE)
        self.profiles = self._load_profiles()
        self.player_key = ""
        self.selected = "Ryu"
        self.confirmed = False
        self.status_message = "SELECT A BARISTA"
        self.status_color = (175, 190, 220)
        self.avatars = {}
        self.background = None
        self.cards = {
            "Ryu": pygame.Rect(90, 170, 340, 365),
            "Kira": pygame.Rect(470, 170, 340, 365),
            "Jax": pygame.Rect(850, 170, 340, 365),
        }
        self.buttons = {}
        self.confirm_button = pygame.Rect(490, 650, 300, 48)
        self.font_big = pygame.font.SysFont("consolas", 40, bold=True)
        self.font_name = pygame.font.SysFont("consolas", 30, bold=True)
        self.font_role = pygame.font.SysFont("consolas", 17, bold=True)
        self.font_body = pygame.font.SysFont("consolas", 15)
        self.font_small = pygame.font.SysFont("consolas", 13)
        self.font_button = pygame.font.SysFont("consolas", 18, bold=True)
        self.font_selected = pygame.font.SysFont("consolas", 22, bold=True)
        self._load_background()
        self._load_avatars()

    @staticmethod
    def _normalise_name(name):
        return " ".join(str(name or "Player").strip().split()).casefold()

    def _new_profile(self):
        return {"unlocked": ["Ryu"], "selected": "Ryu"}

    def _load_profiles(self):
        data = {}
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, dict):
                data = raw
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass

        if isinstance(data.get("players"), dict):
            return {self._normalise_name(k): v for k, v in data["players"].items()}

        migrated = {}
        if any(k in data for k in BARISTAS):
            unlocked = ["Ryu"]
            for name in ("Kira", "Jax"):
                value = data.get(name, False)
                if value is True or value == 1 or value == "unlocked":
                    unlocked.append(name)
            selected = data.get("selected", "Ryu")
            if selected not in BARISTAS:
                selected = "Ryu"
            migrated["lucy"] = {"unlocked": unlocked, "selected": selected}
        return migrated

    def _save_profiles(self):
        payload = {"players": self.profiles}
        tmp = self.save_path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            os.replace(tmp, self.save_path)
        except OSError as error:
            print(f"[BARISTA] Could not save unlocks: {error}")

    def _profile_for(self, player_name):
        self.player_key = self._normalise_name(player_name)
        profile = self.profiles.get(self.player_key)
        if not isinstance(profile, dict):
            profile = self._new_profile()
        unlocked = profile.get("unlocked", ["Ryu"])
        if not isinstance(unlocked, list):
            unlocked = ["Ryu"]
        unlocked = [b for b in BARISTAS if b in unlocked]
        if "Ryu" not in unlocked:
            unlocked.insert(0, "Ryu")
        selected = profile.get("selected", "Ryu")
        if selected not in unlocked:
            selected = "Ryu"
        profile = {"unlocked": unlocked, "selected": selected}
        self.profiles[self.player_key] = profile
        self.selected = selected
        self._save_profiles()
        return profile

    def is_unlocked(self, barista):
        return barista in self.profiles.get(self.player_key, {}).get("unlocked", ["Ryu"])

    def _credits(self):
        try:
            return max(0, int(getattr(self.economy, "credits", 0)))
        except (TypeError, ValueError):
            return 0

    def _spend(self, amount):
        if amount <= 0:
            return True
        credits = self._credits()
        if credits < amount:
            return False
        try:
            self.economy.credits = credits - amount
            if hasattr(self.economy, "save_economy_data"):
                self.economy.save_economy_data()
            return True
        except Exception as error:
            print(f"[BARISTA] Credit update failed: {error}")
            return False

    def _load_background(self):
        path = os.path.join(self.project_root, "assets", "mahirah", "baristas", BACKGROUND_FILE)
        try:
            image = pygame.image.load(path).convert()
            self.background = pygame.transform.smoothscale(image, (self.WIDTH, self.HEIGHT))
        except (pygame.error, FileNotFoundError):
            self.background = None

    def _load_avatars(self):
        avatar_dir = os.path.join(self.project_root, "assets", "mahirah", "baristas")
        for name, info in BARISTA_DATA.items():
            path = os.path.join(avatar_dir, info["avatar"])
            try:
                self.avatars[name] = pygame.image.load(path).convert_alpha()
            except (pygame.error, FileNotFoundError):
                self.avatars[name] = None

    def _draw_glow_rect(self, rect, color, width=2):
        glow = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
        for extra, alpha in ((10, 35), (6, 55), (3, 80)):
            r = pygame.Rect(10 - extra // 2, 10 - extra // 2,
                            rect.width + extra, rect.height + extra)
            pygame.draw.rect(glow, (*color, alpha), r, width + 2, border_radius=14)
        self.screen.blit(glow, (rect.x - 10, rect.y - 10))
        pygame.draw.rect(self.screen, color, rect, width, border_radius=12)

    def _draw_text(self, text, font, color, x, y, center=False):
        surf = font.render(str(text), True, color)
        rect = surf.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(surf, rect)
        return rect

    def _draw_card(self, name, rect):
        info = BARISTA_DATA[name]
        color = info["color"]
        unlocked = self.is_unlocked(name)
        selected = self.selected == name

        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        panel.fill((7, 12, 30, 220))
        self.screen.blit(panel, rect.topleft)
        self._draw_glow_rect(rect, color if selected else tuple(max(35, c // 2) for c in color), 3 if selected else 2)

        avatar = self.avatars.get(name)
        avatar_box = pygame.Rect(rect.x + 20, rect.y + 16, rect.width - 40, 145)
        if avatar is not None:
            iw, ih = avatar.get_size()
            scale = min(avatar_box.width / max(1, iw), avatar_box.height / max(1, ih))
            size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
            img = pygame.transform.smoothscale(avatar, size)
            self.screen.blit(img, img.get_rect(center=avatar_box.center))
        else:
            pygame.draw.rect(self.screen, (15, 22, 45), avatar_box, border_radius=8)
            self._draw_text(name.upper(), self.font_name, color, avatar_box.centerx, avatar_box.centery, True)

        self._draw_text(name.upper(), self.font_name, color, rect.centerx, rect.y + 182, True)
        self._draw_text(info["role"], self.font_role, (210, 220, 240), rect.centerx, rect.y + 211, True)
        self._draw_text("ABILITY", self.font_small, color, rect.x + 24, rect.y + 242)
        self._draw_text(info["ability"], self.font_body, (245, 248, 255), rect.x + 24, rect.y + 263)
        yy = rect.y + 285
        for line in info["description"].splitlines():
            self._draw_text(line, self.font_small, (175, 188, 215), rect.x + 24, yy)
            yy += 18

        btn = pygame.Rect(rect.x + 24, rect.bottom - 48, rect.width - 48, 34)
        self.buttons[name] = btn
        if selected:
            pygame.draw.rect(self.screen, (45, 22, 60), btn, border_radius=7)
            pygame.draw.rect(self.screen, color, btn, 2, border_radius=7)
            self._draw_text("SELECTED", self.font_button, color, btn.centerx, btn.centery, True)
        elif unlocked:
            pygame.draw.rect(self.screen, (18, 55, 55), btn, border_radius=7)
            pygame.draw.rect(self.screen, color, btn, 2, border_radius=7)
            self._draw_text("SELECT", self.font_button, (235, 245, 255), btn.centerx, btn.centery, True)
        else:
            cost = info["cost"]
            can_buy = self._credits() >= cost
            pygame.draw.rect(self.screen, (48, 38, 22) if can_buy else (32, 34, 48), btn, border_radius=7)
            pygame.draw.rect(self.screen, (255, 210, 80) if can_buy else (95, 100, 125), btn, 2, border_radius=7)
            self._draw_text(f"UNLOCK  C {cost:,}", self.font_button,
                            (255, 220, 100) if can_buy else (145, 150, 170),
                            btn.centerx, btn.centery, True)

    def draw(self):
        if self.background is not None:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((5, 8, 22))

        # Dark translucent wash keeps the real city background visible while preserving UI readability.
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((3, 5, 20, 105))
        self.screen.blit(overlay, (0, 0))

        self._draw_text("CHOOSE YOUR", self.font_big, (120, 235, 255), 90, 28)
        self._draw_text("BARISTA", self.font_big, (255, 80, 190), 90, 67)
        self._draw_text("DIFFERENT SKILLS. DIFFERENT PLAYSTYLE.", self.font_role,
                        (220, 235, 255), 455, 45)
        self._draw_text(f"PLAYER: {self.player_key.upper()}", self.font_small,
                        (205, 220, 245), 455, 76)
        self._draw_text(f"CREDITS  {self._credits():,}", self.font_role,
                        (255, 220, 100), 1010, 42)

        for name, rect in self.cards.items():
            self._draw_card(name, rect)

        selected_label = f"SELECTED: {self.selected.upper()}"
        self._draw_text(selected_label, self.font_selected, BARISTA_DATA[self.selected]["color"],
                        640, 565, True)
        self._draw_text(self.status_message, self.font_small, self.status_color, 640, 596, True)

        unlocked = self.is_unlocked(self.selected)
        active = unlocked
        btn_color = (255, 80, 190) if active else (90, 95, 115)
        fill = (55, 20, 70) if active else (30, 32, 45)
        pygame.draw.rect(self.screen, fill, self.confirm_button, border_radius=9)
        pygame.draw.rect(self.screen, btn_color, self.confirm_button, 3 if active else 2, border_radius=9)
        self._draw_text("CONFIRM BARISTA", self.font_button,
                        (255, 240, 255) if active else (145, 150, 170),
                        self.confirm_button.centerx, self.confirm_button.centery, True)

    def _activate(self, name):
        if self.is_unlocked(name):
            self.selected = name
            self.status_message = f"{name.upper()} SELECTED — CLICK CONFIRM BARISTA"
            self.status_color = BARISTA_DATA[name]["color"]
            return True

        cost = BARISTA_DATA[name]["cost"]
        if self._spend(cost):
            if name not in self.profiles[self.player_key]["unlocked"]:
                self.profiles[self.player_key]["unlocked"].append(name)
            self.selected = name
            self.status_message = f"{name.upper()} UNLOCKED — CLICK CONFIRM BARISTA"
            self.status_color = (255, 220, 100)
            self._save_profiles()
            return True

        self.status_message = f"NOT ENOUGH CREDITS TO UNLOCK {name.upper()}"
        self.status_color = (255, 120, 120)
        return False

    def _confirm(self):
        if not self.is_unlocked(self.selected):
            self.status_message = "SELECT AN UNLOCKED BARISTA FIRST"
            self.status_color = (255, 120, 120)
            return None
        self.profiles[self.player_key]["selected"] = self.selected
        self._save_profiles()
        self.confirmed = True
        return self.selected

    def run(self, player_name=None):
        self._profile_for(player_name)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.confirm_button.collidepoint(event.pos):
                        result = self._confirm()
                        if result is not None:
                            return result
                        continue
                    for name, rect in self.cards.items():
                        if rect.collidepoint(event.pos) or self.buttons.get(name, pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                            self._activate(name)
                            break
            self.draw()
            pygame.display.flip()


def choose_barista(screen, economy, player_name):
    return BaristaSelection(screen, economy).run(player_name)


__all__ = ["BaristaSelection", "choose_barista", "BARISTA_DATA"]
