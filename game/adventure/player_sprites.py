import pygame

from game.adventure.asset_loader import (
    load_sprite_sheet,
)
from game.adventure.sprite_sheet import (
    slice_sprite_sheet,
)


class PlayerSprites:
    FRAME_WIDTH = 16
    FRAME_HEIGHT = 32

    SCALE = 3

    DISPLAY_SIZE = (
        FRAME_WIDTH * SCALE,
        FRAME_HEIGHT * SCALE,
    )

    DIRECTION_FRAME_RANGES = {
        "right": (0, 6),
        "up": (6, 12),
        "left": (12, 18),
        "down": (18, 24),
    }

    def __init__(self):
        self.walking = {}
        self.idle = {}

        self._load_sprites()

    def _load_sprites(self):
        walk_sheet = load_sprite_sheet(
            "player/walk_sheet.png"
        )

        idle_sheet = load_sprite_sheet(
            "player/idle_sheet.png"
        )

        if walk_sheet is not None:
            all_walk_frames = slice_sprite_sheet(
                walk_sheet,
                self.FRAME_WIDTH,
                self.FRAME_HEIGHT,
            )

            for direction, frame_range in (
                self.DIRECTION_FRAME_RANGES.items()
            ):
                start, end = frame_range

                direction_frames = (
                    all_walk_frames[start:end]
                )

                self.walking[direction] = [
                    self._scale_frame(frame)
                    for frame in direction_frames
                ]

        if idle_sheet is not None:
            all_idle_frames = slice_sprite_sheet(
                idle_sheet,
                self.FRAME_WIDTH,
                self.FRAME_HEIGHT,
            )

            for direction, frame_range in (
                self.DIRECTION_FRAME_RANGES.items()
            ):
                start, end = frame_range

                direction_frames = (
                    all_idle_frames[start:end]
                )

                self.idle[direction] = [
                    self._scale_frame(frame)
                    for frame in direction_frames
                ]

    def _scale_frame(
        self,
        frame,
    ):
        return pygame.transform.scale(
            frame,
            self.DISPLAY_SIZE,
        )

    def get_walking_frames(
        self,
        direction,
    ):
        return self.walking.get(
            direction,
            [],
        )

    def get_idle_frames(
        self,
        direction,
    ):
        return self.idle.get(
            direction,
            [],
        )

    @staticmethod
    def create_fallback_surface(
        direction,
        size,
    ):
        surface = pygame.Surface(
            size,
            pygame.SRCALPHA,
        )

        body_rect = pygame.Rect(
            7,
            12,
            size[0] - 14,
            size[1] - 16,
        )

        pygame.draw.rect(
            surface,
            (75, 145, 210),
            body_rect,
            border_radius=8,
        )

        pygame.draw.rect(
            surface,
            (225, 230, 240),
            body_rect,
            2,
            border_radius=8,
        )

        center_x = size[0] // 2
        center_y = size[1] // 2

        if direction == "up":
            points = [
                (center_x, center_y - 15),
                (center_x - 7, center_y - 5),
                (center_x + 7, center_y - 5),
            ]

        elif direction == "left":
            points = [
                (center_x - 13, center_y),
                (center_x - 3, center_y - 7),
                (center_x - 3, center_y + 7),
            ]

        elif direction == "right":
            points = [
                (center_x + 13, center_y),
                (center_x + 3, center_y - 7),
                (center_x + 3, center_y + 7),
            ]

        else:
            points = [
                (center_x, center_y + 15),
                (center_x - 7, center_y + 5),
                (center_x + 7, center_y + 5),
            ]

        pygame.draw.polygon(
            surface,
            (245, 205, 110),
            points,
        )

        return surface