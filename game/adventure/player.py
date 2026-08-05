import pygame
from game.adventure.player_sprites import (
    PlayerSprites,
)

class AdventurePlayer:
    def __init__(
        self,
        x,
        y,
        width=28,
        height=32,
        speed=5,
        image=None,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.image = image
        self.sprites = PlayerSprites()

        self.direction = "down"
        self.is_moving = False

        self.animation_frame = 0
        self.animation_timer = pygame.time.get_ticks()
        self.animation_delay = 110

        self.sprite_size = (
            PlayerSprites.DISPLAY_SIZE
        )

        self.facing = "down"

    def _update_animation(self):
        frames = (
            self.sprites.get_walking_frames(
                self.direction
            )
            if self.is_moving
            else self.sprites.get_idle_frames(
                self.direction
            )
        )

        if not frames:
            self.animation_frame = 0
            return

        current_time = pygame.time.get_ticks()

        if (
                current_time
                - self.animation_timer
                >= self.animation_delay
        ):
            self.animation_timer = current_time

            self.animation_frame = (
                                           self.animation_frame + 1
                                   ) % len(frames)

    def _move_horizontal(
            self,
            amount,
            collision_rects,
            bounds,
    ):
        if amount == 0:
            return

        self.rect.x += amount
        self.rect.clamp_ip(bounds)

        for obstacle in collision_rects:
            if not self.rect.colliderect(
                    obstacle
            ):
                continue

            if amount > 0:
                self.rect.right = obstacle.left

            else:
                self.rect.left = obstacle.right

    def _move_vertical(
            self,
            amount,
            collision_rects,
            bounds,
    ):
        if amount == 0:
            return

        self.rect.y += amount
        self.rect.clamp_ip(bounds)

        for obstacle in collision_rects:
            if not self.rect.colliderect(
                    obstacle
            ):
                continue

            if amount > 0:
                self.rect.bottom = obstacle.top

            else:
                self.rect.top = obstacle.bottom

    def handle_input(
            self,
            keys,
            bounds,
            collision_rects=None,
    ):
        collision_rects = (
            collision_rects
            if collision_rects is not None
            else []
        )

        move_x = 0
        move_y = 0

        if keys[pygame.K_a]:
            move_x -= self.speed
            self.direction = "left"

        elif keys[pygame.K_d]:
            move_x += self.speed
            self.direction = "right"

        if keys[pygame.K_w]:
            move_y -= self.speed
            self.direction = "up"

        elif keys[pygame.K_s]:
            move_y += self.speed
            self.direction = "down"

        self.is_moving = (
                move_x != 0
                or move_y != 0
        )

        if move_x != 0 and move_y != 0:
            move_x *= 0.7071
            move_y *= 0.7071

        self._move_horizontal(
            round(move_x),
            collision_rects,
            bounds,
        )

        self._move_vertical(
            round(move_y),
            collision_rects,
            bounds,
        )

        self._update_animation()

    def draw(self, screen):
        if self.is_moving:
            frames = (
                self.sprites.get_walking_frames(
                    self.direction
                )
            )
        else:
            frames = (
                self.sprites.get_idle_frames(
                    self.direction
                )
            )

        image = None

        if frames:
            frame_index = (
                    self.animation_frame
                    % len(frames)
            )

            image = frames[frame_index]

        if image is None:
            image = (
                self.sprites.create_fallback_surface(
                    self.direction,
                    self.sprite_size,
                )
            )

        image_rect = image.get_rect(
            midbottom=(
                self.rect.centerx,
                self.rect.bottom + 4,
            )
        )

        screen.blit(
            image,
            image_rect,
        )