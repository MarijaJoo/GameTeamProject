import pygame

from game.arcade.arcade_settings import (
    ARCADE_ACCENT_COLOR,
)


class KnowledgeDot:
    SIZE = 20
    POINTS = 25

    def __init__(
        self,
        center_x,
        center_y,
        topic,
    ):
        self.topic = topic
        self.collected = False

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

        self.pulse_size = 0
        self.pulse_direction = 1
        self.last_pulse_time = 0

    @property
    def name(self):
        return self.topic["name"]

    @property
    def description(self):
        return self.topic["description"]

    def update(self):
        if self.collected:
            return

        current_time = pygame.time.get_ticks()

        if current_time - self.last_pulse_time < 90:
            return

        self.last_pulse_time = current_time
        self.pulse_size += self.pulse_direction

        if self.pulse_size >= 3:
            self.pulse_direction = -1

        elif self.pulse_size <= 0:
            self.pulse_direction = 1

    def collect(self):
        if self.collected:
            return False

        self.collected = True
        return True

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
            + self.pulse_size
        )

        pygame.draw.circle(
            screen,
            ARCADE_ACCENT_COLOR,
            center,
            radius,
        )

        pygame.draw.circle(
            screen,
            (220, 255, 240),
            center,
            max(3, radius // 2),
        )

        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (
                center[0] - 3,
                center[1] - 3,
            ),
            2,
        )