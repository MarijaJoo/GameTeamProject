import pygame

from game.arcade.arcade_settings import (
    ARCADE_PLAYER_COLOR,
    PLAYER_SIZE,
    PLAYER_SPEED,
)


class ArcadePlayer:
    def __init__(
        self,
        center_x,
        center_y,
    ):
        self.rect = pygame.Rect(
            0,
            0,
            PLAYER_SIZE,
            PLAYER_SIZE,
        )

        self.rect.center = (
            center_x,
            center_y,
        )

        self.speed = PLAYER_SPEED

        self.direction = "right"

    def reset(
        self,
        center_x,
        center_y,
    ):
        self.rect.center = (
            center_x,
            center_y,
        )

        self.direction = "right"

    def handle_input(
        self,
        keys,
        walls,
    ):
        move_x = 0
        move_y = 0

        if keys[pygame.K_a] or keys[
            pygame.K_LEFT
        ]:
            move_x = -self.speed
            self.direction = "left"

        elif keys[pygame.K_d] or keys[
            pygame.K_RIGHT
        ]:
            move_x = self.speed
            self.direction = "right"

        if keys[pygame.K_w] or keys[
            pygame.K_UP
        ]:
            move_y = -self.speed
            self.direction = "up"

        elif keys[pygame.K_s] or keys[
            pygame.K_DOWN
        ]:
            move_y = self.speed
            self.direction = "down"

        # Prevent diagonal movement.
        if move_x != 0 and move_y != 0:
            move_y = 0

        self._move_horizontal(
            move_x,
            walls,
        )

        self._move_vertical(
            move_y,
            walls,
        )

    def _move_horizontal(
        self,
        amount,
        walls,
    ):
        if amount == 0:
            return

        self.rect.x += amount

        for wall in walls:
            if not self.rect.colliderect(
                wall
            ):
                continue

            if amount > 0:
                self.rect.right = wall.left

            else:
                self.rect.left = wall.right

    def _move_vertical(
        self,
        amount,
        walls,
    ):
        if amount == 0:
            return

        self.rect.y += amount

        for wall in walls:
            if not self.rect.colliderect(
                wall
            ):
                continue

            if amount > 0:
                self.rect.bottom = wall.top

            else:
                self.rect.top = wall.bottom

    def draw(
        self,
        screen,
        offset_x,
        offset_y,
    ):
        draw_rect = self.rect.move(
            offset_x,
            offset_y,
        )

        pygame.draw.circle(
            screen,
            ARCADE_PLAYER_COLOR,
            draw_rect.center,
            PLAYER_SIZE // 2,
        )

        pygame.draw.circle(
            screen,
            (255, 245, 165),
            draw_rect.center,
            PLAYER_SIZE // 2,
            2,
        )

        self._draw_direction_marker(
            screen,
            draw_rect,
        )

    def _draw_direction_marker(
        self,
        screen,
        draw_rect,
    ):
        center_x = draw_rect.centerx
        center_y = draw_rect.centery

        if self.direction == "left":
            marker = (
                center_x - 6,
                center_y,
            )

        elif self.direction == "right":
            marker = (
                center_x + 6,
                center_y,
            )

        elif self.direction == "up":
            marker = (
                center_x,
                center_y - 6,
            )

        else:
            marker = (
                center_x,
                center_y + 6,
            )

        pygame.draw.circle(
            screen,
            (35, 70, 90),
            marker,
            3,
        )