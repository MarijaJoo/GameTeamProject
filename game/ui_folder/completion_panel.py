import pygame

from game.localization import t


from game.adventure.settings import (
    COMPLETION_OVERLAY_COLOR,
    HEIGHT,
    SUBTEXT_COLOR,
    TEXT_COLOR,
    WIDTH,
)


class CompletionPanel:
    def __init__(
        self,
        title_font,
        body_font,
    ):
        self.title_font = title_font
        self.body_font = body_font

    def draw_stat(
        self,
        screen,
        label,
        value,
        y,
    ):
        text = self.body_font.render(
            f"{t(label)}: {value}",
            True,
            TEXT_COLOR,
        )

        text_rect = text.get_rect(
            center=(WIDTH // 2, y)
        )

        screen.blit(
            text,
            text_rect,
        )

    def draw(
        self,
        screen,
        report,
    ):
        overlay = pygame.Surface(
            screen.get_size(),
            pygame.SRCALPHA,
        )

        overlay.fill(
            COMPLETION_OVERLAY_COLOR
        )

        screen.blit(
            overlay,
            (0, 0),
        )

        panel = pygame.Rect(
            180,
            90,
            WIDTH - 360,
            HEIGHT - 180,
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

        heading = self.title_font.render(
            t("ДЕНЕШНИОТ ДЕН Е ЗАВРШЕН"),
            True,
            TEXT_COLOR,
        )

        heading_rect = heading.get_rect(
            center=(
                WIDTH // 2,
                panel.y + 55,
            )
        )

        screen.blit(
            heading,
            heading_rect,
        )

        y = panel.y + 125

        self.draw_stat(
            screen,
            t("Освоени поени денес"),
            report["day_score"],
            y,
        )

        y += 42

        self.draw_stat(
            screen,
            t("Вкупен резултат "),
            report["total_score"],
            y,
        )

        y += 42

        self.draw_stat(
            screen,
            t("Точни помошни прашања"),
            (
                f"{report['correct_clues']} / "
                f"{report['total_clues']}"
            ),
            y,
        )

        y += 42

        self.draw_stat(
            screen,
            t("Безбедни конечни одлуки"),
            (
                f"{report['correct_decisions']} / "
                f"{report['total_decisions']}"
            ),
            y,
        )

        y += 42

        self.draw_stat(
            screen,
            t("Максимален резултат за денот"),
            report["maximum_score"],
            y,
        )

        close_text = self.body_font.render(
            t("R: Нов ден     M:  Главно мени     Q:  Излез"),
            True,
            SUBTEXT_COLOR,
        )

        close_rect = close_text.get_rect(
            center=(
                WIDTH // 2,
                panel.bottom - 45,
            )
        )

        screen.blit(
            close_text,
            close_rect,
        )