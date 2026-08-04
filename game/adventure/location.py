import pygame


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

    def add_interactable(self, interactable):
        self.interactables.append(interactable)

    def get_nearby_interactable(self, player_rect):
        for interactable in self.interactables:
            if (
                not interactable.completed
                and interactable.is_near_player(player_rect)
            ):
                return interactable

        return None

    def draw(self, screen, label_font=None):
        pygame.draw.rect(
            screen,
            self.background_color,
            self.bounds,
            border_radius=12,
        )

        if self.background_image:
            scaled_background = pygame.transform.scale(
                self.background_image,
                self.bounds.size,
            )

            screen.blit(
                scaled_background,
                self.bounds.topleft,
            )

        for interactable in self.interactables:
            interactable.draw(
                screen,
                label_font,
            )