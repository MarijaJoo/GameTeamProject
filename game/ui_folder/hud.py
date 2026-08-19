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
            f"Играч: {username}",
            True,
            TEXT_COLOR,
        )

        score_text = self.hud_font.render(
            f"Поени: {score}",
            True,
            TEXT_COLOR,
        )

        connection_mode = (
            "Онлајн"
            if is_online
            else "Офлајн"
        )

        mode_color = (
            ONLINE_COLOR
            if is_online
            else OFFLINE_COLOR
        )

        mode_text = self.body_font.render(
            f"Поврзаност: {connection_mode}",
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
                f"Притисни E за да употребиш "
                f"{interactable.name}"
            )

        elif interactable.interaction_type == "ending":
            prompt_text = (
                "Притисни E за да го завршиш денот"
            )

        else:
            prompt_text = (
                f"Притисни E да погледнеш "
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

    def draw_knowledge_progress(
            self,
            screen,
            collected,
            required,
    ):
        progress_text = self.body_font.render(
            (
                f"Модули за знаење: "
                f"{collected} / {required}"
            ),
            True,
            (245, 220, 120),
        )

        progress_rect = progress_text.get_rect(
            topright = (WIDTH - 25,70,)
        )

        screen.blit(progress_text,progress_rect,)
