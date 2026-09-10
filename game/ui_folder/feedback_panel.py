import pygame

from game.adventure.settings import (
    HEIGHT,
    INCORRECT_COLOR,
    CORRECT_COLOR,
    OVERLAY_COLOR,
    POPUP_COLOR,
    SUBTEXT_COLOR,
    TEXT_COLOR,
    WIDTH,
)

from game.ui_folder.text import (
    draw_wrapped_text,
)
from game.localization import t

class FeedbackPanel:
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
        feedback_message,
        feedback_correct,
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
            170,
            180,
            WIDTH - 340,
            310,
        )

        border_color = (
            CORRECT_COLOR
            if feedback_correct
            else INCORRECT_COLOR
        )

        pygame.draw.rect(
            screen,
            POPUP_COLOR,
            panel,
            border_radius=14,
        )

        pygame.draw.rect(
            screen,
            border_color,
            panel,
            3,
            border_radius=14,
        )

        heading_text = (
            t("ДОБРА ОДЛУКА!")
            if feedback_correct
            else t("ВНИМАВАЈ!")
        )

        heading = self.title_font.render(
            heading_text,
            True,
            border_color,
        )

        heading_rect = heading.get_rect(
            center=(
                panel.centerx,
                panel.y + 55,
            )
        )

        screen.blit(
            heading,
            heading_rect,
        )

        draw_wrapped_text(
            screen,
            t(feedback_message),
            self.body_font,
            TEXT_COLOR,
            panel.x + 40,
            panel.y + 115,
            panel.width - 80,
        )

        instruction = self.body_font.render(
             t("Притисни SPACE за да продолжиш"),
            True,
            SUBTEXT_COLOR,
        )

        instruction_rect = (
            instruction.get_rect(
                center=(
                    panel.centerx,
                    panel.bottom - 35,
                )
            )
        )

        screen.blit(
            instruction,
            instruction_rect,
        )