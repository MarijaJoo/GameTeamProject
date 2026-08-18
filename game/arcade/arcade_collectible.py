import pygame

from game.arcade.arcade_settings import (
    ARCADE_COLLECTIBLE_COLOR,
    COLLECTIBLE_SIZE,
)


class ArcadeCollectible:
    def __init__(
        self,
        center_x,
        center_y,
    ):
        self.collected = False

        self.rect = pygame.Rect(
            0,
            0,
            COLLECTIBLE_SIZE,
            COLLECTIBLE_SIZE,
        )

        self.rect.center = (
            center_x,
            center_y,
        )

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

        draw_center = (
            self.rect.centerx + offset_x,
            self.rect.centery + offset_y,
        )

        pygame.draw.circle(
            screen,
            ARCADE_COLLECTIBLE_COLOR,
            draw_center,
            COLLECTIBLE_SIZE // 2,
        )

        pygame.draw.circle(
            screen,
            (210, 255, 240),
            draw_center,
            max(
                1,
                COLLECTIBLE_SIZE // 4,
            ),
        )