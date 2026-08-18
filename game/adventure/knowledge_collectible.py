import pygame


class KnowledgeCollectible:
    def __init__(
        self,
        x,
        y,
        name,
        description,
        image=None,
        size=(34, 34),
    ):
        self.name = name
        self.description = description
        self.image = image
        self.collected = False

        self.rect = pygame.Rect(
            x,
            y,
            size[0],
            size[1],
        )

        self.animation_offset = 0
        self.animation_direction = 1
        self.last_animation_time = 0

    def update(self):
        if self.collected:
            return

        current_time = pygame.time.get_ticks()

        if (
            current_time
            - self.last_animation_time
            < 80
        ):
            return

        self.last_animation_time = current_time

        self.animation_offset += (
            self.animation_direction
        )

        if self.animation_offset >= 4:
            self.animation_direction = -1

        elif self.animation_offset <= 0:
            self.animation_direction = 1

    def touches_player(self, player_rect):
        return (
            not self.collected
            and self.rect.colliderect(
                player_rect
            )
        )

    def collect(self):
        if self.collected:
            return False

        self.collected = True
        return True

    def draw(self, screen):
        if self.collected:
            return

        draw_rect = self.rect.copy()
        draw_rect.y -= self.animation_offset

        if self.image is not None:
            scaled_image = pygame.transform.scale(
                self.image,
                draw_rect.size,
            )

            screen.blit(
                scaled_image,
                draw_rect,
            )

            return

        # Temporary fallback icon.
        pygame.draw.circle(
            screen,
            (245, 205, 80),
            draw_rect.center,
            draw_rect.width // 2,
        )

        pygame.draw.circle(
            screen,
            (255, 245, 175),
            draw_rect.center,
            draw_rect.width // 2,
            3,
        )

        pygame.draw.circle(
            screen,
            (80, 145, 210),
            draw_rect.center,
            6,
        )