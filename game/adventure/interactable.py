import pygame

DEBUG_COLLISIONS = False
class Interactable:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        name,
        scenario_id=None,
        color=(100, 120, 170),
        image=None,
        interaction_type="scenario",
        target_location=None,
        required_location_complete=None,
        requires_all_scenarios=False,
        show_placeholder=True,
    ):
        self.rect = pygame.Rect(
            x,
            y,
            width,
            height,
        )

        self.show_placeholder = show_placeholder
        self.name = name
        self.scenario_id = scenario_id

        self.color = color
        self.image = image

        self.interaction_type = interaction_type
        self.target_location = target_location

        # Used for locked exits.
        self.required_location_complete = (
            required_location_complete
        )

        # Used by the final “End the Day” interaction.
        self.requires_all_scenarios = (
            requires_all_scenarios
        )

        self.completed = False

    def is_near_player(
        self,
        player_rect,
        distance=45,
    ):
        interaction_area = self.rect.inflate(
            distance * 2,
            distance * 2,
        )

        return interaction_area.colliderect(
            player_rect
        )

    def draw(
        self,
        screen,
        font=None,
    ):
        if self.image:
            scaled_image = pygame.transform.scale(
                self.image,
                self.rect.size,
            )

            screen.blit(
                scaled_image,
                self.rect,
            )


        elif self.show_placeholder:

            draw_color = self.color

            if self.completed:
                draw_color = tuple(
                    max(0, channel - 60)
                    for channel in self.color
                )

            pygame.draw.rect(
                screen,
                draw_color,
                self.rect,
                border_radius=8,
            )

            pygame.draw.rect(
                screen,
                (230, 230, 235),
                self.rect,
                2,
                border_radius=8,
            )

        if font:
            label = font.render(
                self.name,
                True,
                (235, 235, 240),
            )

            label_rect = label.get_rect(
                center=(
                    self.rect.centerx,
                    self.rect.bottom + 20,
                )
            )

            screen.blit(
                label,
                label_rect,
            )

        if DEBUG_COLLISIONS:
            pygame.draw.rect(
                screen,
                (255, 0, 0),
                self.rect,
                2,
            )