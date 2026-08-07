import pygame


class SoftwareUpdate:
    SIZE = 20

    def __init__(
        self,
        center_x,
        center_y,
    ):
        self.rect = pygame.Rect(
            0,
            0,
            self.SIZE,
            self.SIZE,
        )

        self.rect.center = (
            center_x,
            center_y,
        )

        self.collected = False

        self.pulse = 0
        self.pulse_direction = 1
        self.last_pulse_time = 0

    def collect(self):
        if self.collected:
            return False

        self.collected = True
        return True

    def reset(self):
        self.collected = False

    def update(self):
        if self.collected:
            return

        current_time = pygame.time.get_ticks()

        if (
            current_time
            - self.last_pulse_time
            < 80
        ):
            return

        self.last_pulse_time = current_time

        self.pulse += self.pulse_direction

        if self.pulse >= 3:
            self.pulse_direction = -1

        elif self.pulse <= 0:
            self.pulse_direction = 1

    def draw(
        self,
        screen,
        offset_x,
        offset_y,
    ):
        if self.collected:
            return

        center = (
            self.rect.centerx + offset_x,
            self.rect.centery + offset_y,
        )

        radius = (
            self.SIZE // 2
            + self.pulse
        )

        # Outer glow.
        pygame.draw.circle(
            screen,
            (80, 170, 255),
            center,
            radius,
        )

        # Inner circle.
        pygame.draw.circle(
            screen,
            (180, 225, 255),
            center,
            max(4, radius - 4),
        )

        # Simple update arrow.
        font = pygame.font.SysFont(
            "arial",
            15,
            bold=True,
        )

        symbol = font.render(
            "↻",
            True,
            (25, 70, 120),
        )

        symbol_rect = symbol.get_rect(
            center=center
        )

        screen.blit(
            symbol,
            symbol_rect,
        )