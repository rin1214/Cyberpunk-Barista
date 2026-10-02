import os
import pygame


class InstructionScreen:
    WIDTH, HEIGHT = 1280, 720
    FPS = 60

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets", "ui", "how_to_play.png"
        )

        try:
            self.image = pygame.image.load(path).convert_alpha()
        except (pygame.error, FileNotFoundError):
            self.image = None
            print("[INSTRUCTIONS] how_to_play.png not found.")

    def button_rect(self):
        w, h = self.screen.get_size()

        # START ORDER area on the 1280x720 artwork
        return pygame.Rect(
            int(w * 0.24),
            int(h * 0.875),
            int(w * 0.52),
            int(h * 0.12)
        )

    def draw(self):
        w, h = self.screen.get_size()

        if self.image:
            image = pygame.transform.smoothscale(
                self.image, (w, h)
            )
            self.screen.blit(image, (0, 0))
        else:
            self.screen.fill((8, 7, 20))

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    return False

                if event.type == pygame.KEYDOWN:
                    if event.key in (
                        pygame.K_RETURN,
                        pygame.K_KP_ENTER,
                        pygame.K_SPACE
                    ):
                        return True

                    if event.key == pygame.K_ESCAPE:
                        return False

                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and self.button_rect().collidepoint(event.pos)
                ):
                    return True

            self.draw()
            self.clock.tick(self.FPS)