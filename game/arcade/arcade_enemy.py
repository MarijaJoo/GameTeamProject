import random

import pygame

from game.arcade.arcade_settings import (
    TILE_SIZE,
)


class VirusEnemy:
    SIZE = 22
    SPEED = 2

    DIRECTIONS = {
        "left": (-1, 0),
        "right": (1, 0),
        "up": (0, -1),
        "down": (0, 1),
    }

    OPPOSITE = {
        "left": "right",
        "right": "left",
        "up": "down",
        "down": "up",
    }

    def __init__(
        self,
        center_x,
        center_y,
    ):
        self.spawn = (
            center_x,
            center_y,
        )

        self.rect = pygame.Rect(
            0,
            0,
            self.SIZE,
            self.SIZE,
        )
        self.active = True

        self.respawn_delay = 5000
        self.respawn_at = 0

        self.rect.center = self.spawn

        self.direction = random.choice(
            list(self.DIRECTIONS.keys())
        )

        self.target_center = self.spawn

    def reset(self):
        self.rect.center = self.spawn

        self.direction = random.choice(
            list(self.DIRECTIONS.keys())
        )

        self.target_center = self.spawn

        self.active = True
        self.respawn_at = 0

    def update(
        self,
        walls,
    ):
        if not self.active:
            if (
                    pygame.time.get_ticks()
                    >= self.respawn_at
            ):
                self.reset()

            return
        if self.rect.center == self.target_center:
            self._choose_next_target(
                walls
            )

        self._move_toward_target()

    def _choose_next_target(
        self,
        walls,
    ):
        current_x, current_y = (
            self.rect.center
        )

        valid_directions = []

        for (
            direction,
            (dx, dy),
        ) in self.DIRECTIONS.items():
            candidate_center = (
                current_x
                + dx * TILE_SIZE,
                current_y
                + dy * TILE_SIZE,
            )

            if not self._is_wall(
                candidate_center,
                walls,
            ):
                valid_directions.append(
                    direction
                )

        if not valid_directions:
            return

        opposite = self.OPPOSITE.get(
            self.direction
        )

        preferred = [
            direction
            for direction in valid_directions
            if direction != opposite
        ]

        if preferred:
            valid_directions = preferred

        self.direction = random.choice(
            valid_directions
        )

        dx, dy = self.DIRECTIONS[
            self.direction
        ]

        self.target_center = (
            current_x
            + dx * TILE_SIZE,
            current_y
            + dy * TILE_SIZE,
        )

    @staticmethod
    def _is_wall(
        center,
        walls,
    ):
        return any(
            wall.collidepoint(center)
            for wall in walls
        )

    def _move_toward_target(self):
        current_x, current_y = (
            self.rect.center
        )

        target_x, target_y = (
            self.target_center
        )

        if current_x < target_x:
            current_x = min(
                current_x + self.SPEED,
                target_x,
            )

        elif current_x > target_x:
            current_x = max(
                current_x - self.SPEED,
                target_x,
            )

        elif current_y < target_y:
            current_y = min(
                current_y + self.SPEED,
                target_y,
            )

        elif current_y > target_y:
            current_y = max(
                current_y - self.SPEED,
                target_y,
            )

        self.rect.center = (
            current_x,
            current_y,
        )

    def neutralize(self):
        if not self.active:
            return False

        self.active = False

        self.respawn_at = (
                pygame.time.get_ticks()
                + self.respawn_delay
        )

        return True

    def draw(
            self,
            screen,
            offset_x,
            offset_y,
            vulnerable=False,
    ):
        if not self.active:
            return

        draw_rect = self.rect.move(
            offset_x,
            offset_y,
        )

        # Virus changes color while the
        # Software Update is active.
        if vulnerable:
            body_color = (70, 165, 245)
            border_color = (35, 90, 160)

        else:
            body_color = (220, 70, 85)
            border_color = (120, 35, 50)

        pygame.draw.circle(
            screen,
            body_color,
            draw_rect.center,
            self.SIZE // 2,
        )

        pygame.draw.circle(
            screen,
            border_color,
            draw_rect.center,
            self.SIZE // 2,
            2,
        )

        # Eyes.
        eye_y = (
                draw_rect.centery - 3
        )

        pygame.draw.circle(
            screen,
            (245, 245, 245),
            (
                draw_rect.centerx - 4,
                eye_y,
            ),
            3,
        )

        pygame.draw.circle(
            screen,
            (245, 245, 245),
            (
                draw_rect.centerx + 4,
                eye_y,
            ),
            3,
        )

        pygame.draw.circle(
            screen,
            (35, 35, 45),
            (
                draw_rect.centerx - 4,
                eye_y,
            ),
            1,
        )

        pygame.draw.circle(
            screen,
            (35, 35, 45),
            (
                draw_rect.centerx + 4,
                eye_y,
            ),
            1,
        )
