import pygame

from game.localization import t

from game.adventure.settings import (
    HEIGHT,
    SUBTEXT_COLOR,
    TEXT_COLOR,
    WIDTH,
)


class DayIntroPanel:
    def __init__(
        self,
        title_font,
        body_font,
    ):
        self.title_font = title_font
        self.body_font = body_font

    def draw(self, screen):
        # Dark transparent overlay
        overlay = pygame.Surface(
            screen.get_size(),
            pygame.SRCALPHA,
        )

        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        # Popup
        panel = pygame.Rect(
            140,
            170,
            WIDTH - 280,
            330,
        )

        pygame.draw.rect(
            screen,
            (42, 48, 66),
            panel,
            border_radius=16,
        )

        pygame.draw.rect(
            screen,
            (90, 170, 230),
            panel,
            3,
            border_radius=16,
        )

        # Title
        title = self.title_font.render(
            t("НОВ ДЕН"),
            True,
            TEXT_COLOR,
        )

        title_rect = title.get_rect(
            center=(WIDTH // 2, panel.y + 55)
        )

        screen.blit(
            title,
            title_rect,
        )

        # Main message
        message = (
            "Сега треба да ги завршиш сите дијалози "
            "во секоја соба и да одговориш на прашањата "
            "за да освоиш поени."
        )

        self._draw_wrapped_text(
            screen,
            t(message),
            panel.x + 45,
            panel.y + 115,
            panel.width - 90,
        )

        # Continue instruction
        instruction = self.body_font.render(
            t("Притисни SPACE за да продолжиш"),
            True,
            SUBTEXT_COLOR,
        )

        instruction_rect = instruction.get_rect(
            center=(WIDTH // 2, panel.bottom - 45)
        )

        screen.blit(
            instruction,
            instruction_rect,
        )

    def _draw_wrapped_text(
        self,
        screen,
        text,
        x,
        y,
        max_width,
    ):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = (
                word
                if not current_line
                else current_line + " " + word
            )

            if (
                self.body_font.size(test_line)[0]
                <= max_width
            ):
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        line_height = self.body_font.get_height() + 8

        for line in lines:
            rendered = self.body_font.render(
                line,
                True,
                TEXT_COLOR,
            )

            screen.blit(
                rendered,
                (x, y),
            )

            y += line_height