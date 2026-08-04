import pygame

from game.adventure.settings import (
    HEIGHT,
    OFFLINE_COLOR,
    ONLINE_COLOR,
    PROMPT_BACKGROUND_COLOR,
    TEXT_COLOR,
    WIDTH,
)


class AdventureHUD:
    def __init__(
        self,
        hud_font,
        body_font,
    ):
        self.hud_font = hud_font
        self.body_font = body_font

    def draw(
        self,
        screen,
        username,
        score,
        is_online,
        location_name,
    ):
        username_text = self.hud_font.render(
            f"Player: {username}",
            True,
            TEXT_COLOR,
        )

        score_text = self.hud_font.render(
            f"Score: {score}",
            True,
            TEXT_COLOR,
        )

        connection_mode = (
            "ONLINE"
            if is_online
            else "OFFLINE"
        )

        mode_color = (
            ONLINE_COLOR
            if is_online
            else OFFLINE_COLOR
        )

        mode_text = self.body_font.render(
            f"Mode: {connection_mode}",
            True,
            mode_color,
        )

        location_text = self.hud_font.render(
            location_name,
            True,
            TEXT_COLOR,
        )

        screen.blit(
            username_text,
            (30, 25),
        )

        screen.blit(
            score_text,
            (
                WIDTH
                - score_text.get_width()
                - 30,
                25,
            ),
        )

        screen.blit(
            mode_text,
            (
                WIDTH // 2
                - mode_text.get_width() // 2,
                28,
            ),
        )

        location_rect = (
            location_text.get_rect(
                center=(
                    WIDTH // 2,
                    78,
                )
            )
        )

        screen.blit(
            location_text,
            location_rect,
        )

    def draw_interaction_prompt(
            self,
            screen,
            interactable,
    ):
        if interactable is None:
            return

        if interactable.interaction_type == "location":
            prompt_text = (
                f"Press E to use "
                f"{interactable.name}"
            )

        elif interactable.interaction_type == "ending":
            prompt_text = (
                "Press E to end the day"
            )

        else:
            prompt_text = (
                f"Press E to inspect "
                f"{interactable.name}"
            )

        prompt = self.body_font.render(
            prompt_text,
            True,
            TEXT_COLOR,
        )

        prompt_rect = prompt.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT - 30,
            )
        )

        pygame.draw.rect(
            screen,
            PROMPT_BACKGROUND_COLOR,
            prompt_rect.inflate(30, 16),
            border_radius=8,
        )

        screen.blit(
            prompt,
            prompt_rect,
        )