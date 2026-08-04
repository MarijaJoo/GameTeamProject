import pygame


class AdventurePlayer:
    def __init__(
        self,
        x,
        y,
        width=42,
        height=42,
        speed=5,
        image=None,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.image = image

        self.facing = "down"

    def handle_input(self, keys, bounds):
        movement_x = 0
        movement_y = 0

        if keys[pygame.K_a]:
            movement_x -= self.speed
            self.facing = "left"

        if keys[pygame.K_d]:
            movement_x += self.speed
            self.facing = "right"

        if keys[pygame.K_w]:
            movement_y -= self.speed
            self.facing = "up"

        if keys[pygame.K_s]:
            movement_y += self.speed
            self.facing = "down"

        self.rect.x += movement_x
        self.rect.y += movement_y
        self.rect.clamp_ip(bounds)

    def draw(self, screen):
        if self.image:
            scaled_image = pygame.transform.scale(
                self.image,
                self.rect.size,
            )
            screen.blit(scaled_image, self.rect)
        else:
            pygame.draw.rect(
                screen,
                (55, 150, 220),
                self.rect,
                border_radius=8,
            )