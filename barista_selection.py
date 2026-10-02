from __future__ import annotations

import json
import math
import os
import time

import pygame

# ── Barista roster ─────────────────────────────────────────────────────────────
BARISTA_DATA = {
    "Ryu": {
        "cost": 0,
        "color": (75, 225, 255),
        "role": "ROOKIE BARISTA",
        "ability": "BALANCED",
        "description": "No special bonus, but reliable\nin all situations.",
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

BARISTAS        = ("Ryu", "Kira", "Jax")
SAVE_FILE       = "barista_unlocks.json"
BACKGROUND_FILE = "barista_selection_bg.jpg"

# ── Shared palette (mirrors MixingStation) ─────────────────────────────────────
_CYAN   = (75,  225, 255)
_PINK   = (255, 80,  190)
_YELLOW = (255, 220, 100)
_GREEN  = (90,  235, 165)
_WHITE  = (245, 248, 255)
_MUTED  = (125, 140, 170)
_DARK   = (5,   8,   22)


class BaristaSelection:
    """Barista selection screen — on-theme with the game's cyberpunk aesthetic."""

    WIDTH, HEIGHT = 1280, 720

    def __init__(self, screen, economy=None):
        self.screen  = screen
        self.economy = economy
        self.root    = os.path.dirname(os.path.abspath(__file__))
        self.save_path = os.path.join(self.root, SAVE_FILE)

        self.profiles     = self._load_profiles()
        self.player_key   = ""
        self.selected     = "Ryu"
        self.confirmed    = False
        self.status_message = "SELECT A BARISTA"
        self.status_color   = _MUTED

        self.avatars    = {}
        self.background = None
        self.buttons    = {}
        self._t0 = time.monotonic()   # for pulse animations

        # Card layout – three equal cards spanning the width
        cw, ch = 330, 390
        self.cards = {
            "Ryu":  pygame.Rect(65,  145, cw, ch),
            "Kira": pygame.Rect(475, 145, cw, ch),
            "Jax":  pygame.Rect(885, 145, cw, ch),
        }
        cx = self.WIDTH // 2
        self.confirm_button = pygame.Rect(cx - 175, 648, 350, 52)

        self._init_fonts()
        self._load_background()
        self._load_avatars()

    # ── Fonts ──────────────────────────────────────────────────────────────────

    def _init_fonts(self):
        pygame.font.init()
        font_dir = os.path.join(self.root, "assets", "fonts")
        bold_path = med_path = None
        for fn in ["Orbitron-Bold.ttf", "Orbitron-Black.ttf"]:
            p = os.path.join(font_dir, fn)
            if os.path.isfile(p) and bold_path is None:
                bold_path = p
        for fn in ["Orbitron-Medium.ttf", "Orbitron-Light.ttf"]:
            p = os.path.join(font_dir, fn)
            if os.path.isfile(p) and med_path is None:
                med_path = p

        def F(path, size):
            try:
                return pygame.font.Font(path, size)
            except Exception:
                return pygame.font.SysFont("consolas", size, bold=True)

        self.font_title    = F(bold_path, 40)   # "CHOOSE YOUR BARISTA"
        self.font_tagline  = F(med_path,  13)   # sub-header
        self.font_credits  = F(bold_path, 14)   # credits chip
        self.font_name     = F(bold_path, 22)   # barista name
        self.font_role     = F(med_path,  12)   # role text
        self.font_label    = F(bold_path, 10)   # "ABILITY" micro tag
        self.font_ability  = F(bold_path, 13)   # ability name
        self.font_desc     = F(med_path,  12)   # description lines
        self.font_btn      = F(bold_path, 13)   # card button
        self.font_confirm  = F(bold_path, 17)   # confirm button
        self.font_selected = F(bold_path, 16)   # selected banner
        self.font_status   = F(med_path,  12)   # status message

    # ── Save / load ────────────────────────────────────────────────────────────

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
                v = data.get(name, False)
                if v is True or v == 1 or v == "unlocked":
                    unlocked.append(name)
            sel = data.get("selected", "Ryu")
            if sel not in BARISTAS:
                sel = "Ryu"
            migrated["lucy"] = {"unlocked": unlocked, "selected": sel}
        return migrated

    def _save_profiles(self):
        tmp = self.save_path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"players": self.profiles}, f, indent=2)
            os.replace(tmp, self.save_path)
        except OSError as e:
            print(f"[BARISTA] Save failed: {e}")

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
        sel = profile.get("selected", "Ryu")
        if sel not in unlocked:
            sel = "Ryu"
        profile = {"unlocked": unlocked, "selected": sel}
        self.profiles[self.player_key] = profile
        self.selected = sel
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
        c = self._credits()
        if c < amount:
            return False
        try:
            self.economy.credits = c - amount
            if hasattr(self.economy, "save_economy_data"):
                self.economy.save_economy_data()
            return True
        except Exception as e:
            print(f"[BARISTA] Credit update failed: {e}")
            return False

    # ── Assets ─────────────────────────────────────────────────────────────────

    def _load_background(self):
        path = os.path.join(self.root, "assets", "baristas", BACKGROUND_FILE)
        try:
            self.background = pygame.transform.smoothscale(
                pygame.image.load(path).convert(), (self.WIDTH, self.HEIGHT))
        except (pygame.error, FileNotFoundError):
            self.background = None

    def _load_avatars(self):
        d = os.path.join(self.root, "assets", "baristas")
        for name, info in BARISTA_DATA.items():
            try:
                self.avatars[name] = pygame.image.load(
                    os.path.join(d, info["avatar"])).convert_alpha()
            except (pygame.error, FileNotFoundError):
                self.avatars[name] = None

    # ── Draw helpers ───────────────────────────────────────────────────────────

    def _pulse(self, speed=2.0, lo=0.5, hi=1.0):
        t = time.monotonic() - self._t0
        return lo + (hi - lo) * (0.5 + 0.5 * math.sin(t * speed * math.pi))

    def _blit(self, text, font, color, x, y, center=False, alpha=255):
        surf = font.render(str(text), True, color)
        if alpha < 255:
            surf.set_alpha(alpha)
        r = surf.get_rect()
        if center:
            r.center = (x, y)
        else:
            r.topleft = (x, y)
        self.screen.blit(surf, r)
        return r

    def _glow_rect(self, rect, color, border=2, pulse=1.0, radius=12):
        s = pygame.Surface((rect.width + 28, rect.height + 28), pygame.SRCALPHA)
        for extra, base_a in ((12, 20), (7, 40), (3, 65)):
            a = int(base_a * pulse)
            r = pygame.Rect(14 - extra // 2, 14 - extra // 2,
                            rect.width + extra, rect.height + extra)
            pygame.draw.rect(s, (*color, a), r, border + 2, border_radius=radius + 4)
        self.screen.blit(s, (rect.x - 14, rect.y - 14))
        pygame.draw.rect(self.screen, color, rect, border, border_radius=radius)

    def _panel(self, rect, fill=(7, 12, 30), fill_alpha=215, radius=12):
        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        s.fill((*fill, fill_alpha))
        self.screen.blit(s, rect.topleft)
        # subtle inner top-edge highlight
        hi = pygame.Surface((rect.width - 4, 2), pygame.SRCALPHA)
        hi.fill((255, 255, 255, 18))
        self.screen.blit(hi, (rect.x + 2, rect.y + 1))

    def _scanlines(self, rect, alpha=15):
        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        for y in range(0, rect.height, 4):
            pygame.draw.line(s, (0, 0, 0, alpha), (0, y), (rect.width, y))
        self.screen.blit(s, rect.topleft)

    # ── Card ───────────────────────────────────────────────────────────────────

    def _draw_card(self, name, rect):
        info     = BARISTA_DATA[name]
        color    = info["color"]
        unlocked = self.is_unlocked(name)
        is_sel   = (self.selected == name)
        pulse    = self._pulse() if is_sel else 0.35

        # Background panel
        bg = (10, 18, 40) if is_sel else (7, 12, 30)
        self._panel(rect, fill=bg, fill_alpha=218)

        # Glow border – bright when selected, dim otherwise
        bcolor = color if is_sel else tuple(max(25, c // 3) for c in color)
        bw     = 2 if is_sel else 1
        self._glow_rect(rect, bcolor, border=bw, pulse=pulse)

        # Scanline overlay for CRT feel
        self._scanlines(rect, alpha=18 if is_sel else 12)

        # Top accent stripe when selected
        if is_sel:
            stripe = pygame.Surface((rect.width, 3), pygame.SRCALPHA)
            stripe.fill((*color, 210))
            self.screen.blit(stripe, rect.topleft)

        # ── Avatar (large upper half of card)
        av_box = pygame.Rect(rect.x + 14, rect.y + 12, rect.width - 28, 185)
        avatar = self.avatars.get(name)
        if avatar:
            iw, ih = avatar.get_size()
            scale  = min(av_box.width / max(1, iw), av_box.height / max(1, ih))
            img    = pygame.transform.smoothscale(avatar, (max(1, int(iw * scale)),
                                                            max(1, int(ih * scale))))
            if not unlocked:
                img.set_alpha(50)
            self.screen.blit(img, img.get_rect(center=av_box.center))
        else:
            pygame.draw.rect(self.screen, (15, 22, 45), av_box, border_radius=8)
            self._blit(name[0], self.font_name, color,
                       av_box.centerx, av_box.centery, center=True)

        # Lock icon when locked
        if not unlocked:
            self._blit("[ LOCKED ]", self.font_label, (160, 170, 200),
                       av_box.centerx, av_box.centery, center=True)

        # ── Divider under avatar
        div_y = rect.y + 204
        pygame.draw.line(self.screen, (*color, 80 if is_sel else 35),
                         (rect.x + 18, div_y), (rect.right - 18, div_y), 1)

        # ── Name + role
        self._blit(name.upper(), self.font_name, color,
                   rect.centerx, div_y + 16, center=True)
        self._blit(info["role"], self.font_role, _MUTED,
                   rect.centerx, div_y + 38, center=True)

        # ── Ability section
        ab_y = div_y + 60
        # micro label with underline
        lr = self._blit("ABILITY", self.font_label, color, rect.x + 20, ab_y)
        pygame.draw.line(self.screen, color,
                         (rect.x + 20, lr.bottom + 1),
                         (rect.x + 20 + lr.width, lr.bottom + 1), 1)
        self._blit(info["ability"], self.font_ability, _WHITE, rect.x + 20, ab_y + 14)

        # ── Description
        dy = ab_y + 36
        for line in info["description"].splitlines():
            self._blit(line, self.font_desc, _MUTED, rect.x + 20, dy)
            dy += 18

        # ── Card button
        btn = pygame.Rect(rect.x + 18, rect.bottom - 52, rect.width - 36, 38)
        self.buttons[name] = btn

        if is_sel:
            gf = pygame.Surface(btn.size, pygame.SRCALPHA)
            gf.fill((*color, int(30 * self._pulse())))
            self.screen.blit(gf, btn.topleft)
            pygame.draw.rect(self.screen, color, btn, 2, border_radius=8)
            self._blit("SELECTED", self.font_btn, color,
                       btn.centerx, btn.centery, center=True)
        elif unlocked:
            pygame.draw.rect(self.screen, (12, 40, 50), btn, border_radius=8)
            pygame.draw.rect(self.screen, color, btn, 2, border_radius=8)
            self._blit("SELECT", self.font_btn, _WHITE,
                       btn.centerx, btn.centery, center=True)
        else:
            cost    = info["cost"]
            can_buy = self._credits() >= cost
            fc      = (48, 36, 10) if can_buy else (28, 30, 44)
            bc      = _YELLOW      if can_buy else (72, 76, 105)
            tc      = _YELLOW      if can_buy else (105, 110, 135)
            pygame.draw.rect(self.screen, fc, btn, border_radius=8)
            pygame.draw.rect(self.screen, bc, btn, 2, border_radius=8)
            self._blit(f"UNLOCK  CREDITS {cost:,}", self.font_btn, tc,
                       btn.centerx, btn.centery, center=True)

    # ── Full draw ──────────────────────────────────────────────────────────────

    def draw(self):
        # Background
        if self.background is not None:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(_DARK)

        # Global dark tint for readability
        tint = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        tint.fill((3, 5, 18, 115))
        self.screen.blit(tint, (0, 0))

        # ── Header bar
        hdr = pygame.Surface((self.WIDTH, 125), pygame.SRCALPHA)
        hdr.fill((4, 8, 22, 172))
        self.screen.blit(hdr, (0, 0))
        pygame.draw.line(self.screen, (*_CYAN, 55), (0, 124), (self.WIDTH, 124), 1)

        # Title
        self._blit("CHOOSE YOUR", self.font_title, _CYAN,  72, 26)
        self._blit("BARISTA",     self.font_title, _PINK,  72, 70)

        # Tagline + player name
        self._blit("DIFFERENT SKILLS.  DIFFERENT PLAYSTYLE.",
                   self.font_tagline, (210, 225, 250), 445, 42)
        self._blit(f"PLAYER:  {self.player_key.upper()}",
                   self.font_tagline, _MUTED, 445, 68)

        # Credits chip (top-right)
        cred_txt  = f"CREDITS  {self._credits():,}"
        cs        = self.font_credits.render(cred_txt, True, _YELLOW)
        chip_w    = cs.get_width() + 28
        chip_r    = pygame.Rect(self.WIDTH - chip_w - 22, 42, chip_w, 32)
        pygame.draw.rect(self.screen, (38, 28, 4),  chip_r, border_radius=6)
        pygame.draw.rect(self.screen, _YELLOW, chip_r, 2, border_radius=6)
        self.screen.blit(cs, cs.get_rect(center=chip_r.center))

        # ── Cards
        for name, rect in self.cards.items():
            self._draw_card(name, rect)

        # ── Selected banner
        sel_c = BARISTA_DATA[self.selected]["color"]
        self._blit(f"SELECTED:  {self.selected.upper()}",
                   self.font_selected, sel_c, self.WIDTH // 2, 560, center=True)
        self._blit(self.status_message, self.font_status, self.status_color,
                   self.WIDTH // 2, 585, center=True)

        # ── Confirm button
        active = self.is_unlocked(self.selected)
        bc     = _PINK if active else (72, 75, 105)
        fc     = (50, 14, 62) if active else (24, 26, 38)
        pygame.draw.rect(self.screen, fc, self.confirm_button, border_radius=10)
        pygame.draw.rect(self.screen, bc, self.confirm_button, 2, border_radius=10)
        if active:
            p  = self._pulse(speed=1.8, lo=0.4, hi=1.0)
            gs = pygame.Surface(self.confirm_button.size, pygame.SRCALPHA)
            gs.fill((*_PINK, int(26 * p)))
            self.screen.blit(gs, self.confirm_button.topleft)
        tc = _WHITE if active else (120, 125, 155)
        self._blit("CONFIRM BARISTA", self.font_confirm, tc,
                   self.confirm_button.centerx, self.confirm_button.centery, center=True)

    # ── Interaction ────────────────────────────────────────────────────────────

    def _activate(self, name):
        if self.is_unlocked(name):
            self.selected       = name
            self.status_message = f"{name.upper()} SELECTED — CLICK CONFIRM"
            self.status_color   = BARISTA_DATA[name]["color"]
            return True
        cost = BARISTA_DATA[name]["cost"]
        if self._spend(cost):
            if name not in self.profiles[self.player_key]["unlocked"]:
                self.profiles[self.player_key]["unlocked"].append(name)
            self.selected       = name
            self.status_message = f"{name.upper()} UNLOCKED — CLICK CONFIRM"
            self.status_color   = _YELLOW
            self._save_profiles()
            return True
        self.status_message = f"NOT ENOUGH CREDITS TO UNLOCK {name.upper()}"
        self.status_color   = (255, 120, 120)
        return False

    def _confirm(self):
        if not self.is_unlocked(self.selected):
            self.status_message = "SELECT AN UNLOCKED BARISTA FIRST"
            self.status_color   = (255, 120, 120)
            return None
        self.profiles[self.player_key]["selected"] = self.selected
        self._save_profiles()
        self.confirmed = True
        return self.selected

    def run(self, player_name=None):
        self._profile_for(player_name)
        clock = pygame.time.Clock()
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
                        if rect.collidepoint(event.pos) or \
                           self.buttons.get(name, pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                            self._activate(name)
                            break
            self.draw()
            pygame.display.flip()
            clock.tick(60)


def choose_barista(screen, economy, player_name):
    return BaristaSelection(screen, economy).run(player_name)


__all__ = ["BaristaSelection", "choose_barista", "BARISTA_DATA"]

