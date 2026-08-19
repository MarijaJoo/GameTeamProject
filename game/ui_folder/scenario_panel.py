import pygame

from game.adventure.settings import (
    ANSWER_BORDER_COLOR,
    ANSWER_BOX_COLOR,
    HEIGHT,
    OVERLAY_COLOR,
    POPUP_BORDER,
    POPUP_COLOR,
    SUBTEXT_COLOR,
    TEXT_COLOR,
    WIDTH,
)

from game.ui_folder.text import (
    draw_wrapped_text,
)


class ScenarioPanel:
    def __init__(
        self,
        title_font,
        body_font,
    ):
        self.title_font = title_font
        self.body_font = body_font

    def draw(
        self,
        screen,
        scenario,
    ):
        overlay = pygame.Surface(
            screen.get_size(),
            pygame.SRCALPHA,
        )

        overlay.fill(
            OVERLAY_COLOR
        )

        screen.blit(
            overlay,
            (0, 0),
        )

        panel = pygame.Rect(
            120,
            90,
            WIDTH - 240,
            HEIGHT - 180,
        )

        pygame.draw.rect(
            screen,
            POPUP_COLOR,
            panel,
            border_radius=14,
        )

        pygame.draw.rect(
            screen,
            POPUP_BORDER,
            panel,
            3,
            border_radius=14,
        )

        title = self.title_font.render(
            scenario["npc_name"],
            True,
            TEXT_COLOR,
        )

        title_rect = title.get_rect(
            center=(
                panel.centerx,
                panel.y + 45,
            )
        )

        screen.blit(
            title,
            title_rect,
        )

        y = draw_wrapped_text(
            screen,
            scenario["description"],
            self.body_font,
            TEXT_COLOR,
            panel.x + 40,
            panel.y + 95,
            panel.width - 80,
        )

        y += 20

        actions = scenario.get(
            "actions",
            [],
        )

        for index, action in enumerate(
            actions[:2]
        ):
            answer_box = pygame.Rect(
                panel.x + 40,
                y,
                panel.width - 80,
                70,
            )

            pygame.draw.rect(
                screen,
                ANSWER_BOX_COLOR,
                answer_box,
                border_radius=9,
            )

            pygame.draw.rect(
                screen,
                ANSWER_BORDER_COLOR,
                answer_box,
                2,
                border_radius=9,
            )

            answer_text = (
                f"{index + 1}. "
                f"{action['action_text']}"
            )

            draw_wrapped_text(
                screen,
                answer_text,
                self.body_font,
                TEXT_COLOR,
                answer_box.x + 16,
                answer_box.y + 14,
                answer_box.width - 32,
            )

            y += 85

        instruction = self.body_font.render(
            "Притисни 1 или 2 за да избереш",
            True,
            SUBTEXT_COLOR,
        )

        instruction_rect = (
            instruction.get_rect(
                center=(
                    panel.centerx,
                    panel.bottom - 30,
                )
            )
        )

        screen.blit(
            instruction,
            instruction_rect,
        )
