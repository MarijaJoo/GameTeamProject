import pygame

from game.adventure.interactable import DEBUG_COLLISIONS
from game.adventure.knowledge_collectible import (
    KnowledgeCollectible,
)

class AdventureLocation:
    def __init__(
        self,
        name,
        bounds,
        player_spawn,
        background_color=(52, 61, 82),
        background_image=None,
    ):
        self.name = name
        self.bounds = pygame.Rect(bounds)
        self.player_spawn = player_spawn

        self.background_color = background_color
        self.background_image = background_image

        self.interactables = []
        self.collision_rects = []
        self.collectibles = []

    def add_interactable(self, interactable):
        self.interactables.append(interactable)

    def add_collectible(self, collectible):
        self.collectibles.append(
            collectible
        )

    def get_colliding_collectible(
            self,
            player_rect,
    ):
        for collectible in self.collectibles:
            if collectible.touches_player(
                    player_rect
            ):
                return collectible

        return None

    def update_collectibles(self):
        for collectible in self.collectibles:
            collectible.update()

    def add_collision(
        self,
        x,
        y,
        width,
        height,
    ):
        self.collision_rects.append(
            pygame.Rect(
                x,
                y,
                width,
                height,
            )
        )

    def get_nearby_interactable(
        self,
        player_rect,
    ):
        for interactable in self.interactables:
            if (
                not interactable.completed
                and interactable.is_near_player(
                    player_rect
                )
            ):
                return interactable

        return None

    def draw(
            self,
            screen,
            label_font=None,
    ):
        pygame.draw.rect(
            screen,
            self.background_color,
            self.bounds,
            border_radius=12,
        )

        if self.background_image is not None:
            screen.blit(
                self.background_image,
                self.bounds.topleft,
            )

        for collectible in self.collectibles:
            collectible.draw(screen)

        for interactable in self.interactables:
            interactable.draw(
                screen,
                label_font,
            )

        # Optional collision debugging.
        if DEBUG_COLLISIONS:
            for collision_rect in self.collision_rects:
                pygame.draw.rect(
                    screen,
                    (255, 0, 0),
                    collision_rect,
                    2,
                )