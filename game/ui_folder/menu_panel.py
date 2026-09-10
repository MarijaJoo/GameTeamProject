import pygame
from game.localization.localization import t

from game.adventure.settings import (
    BACKGROUND_COLOR,
    SUBTEXT_COLOR,
    TEXT_COLOR,
    WIDTH,
    HEIGHT,
)


class MenuPanel:
    OPTIONS = [
        "Почни нов ден",
        "Како се игра",
        "Излези",
    ]

    def __init__(
        self,
        title_font,
        body_font,
    ):
        self.title_font = title_font
        self.body_font = body_font
        self.selected_index = 0

    def move_up(self):
        self.selected_index = (
            self.selected_index - 1
        ) % len(self.OPTIONS)

    def move_down(self):
        self.selected_index = (
            self.selected_index + 1
        ) % len(self.OPTIONS)

    def get_selected_option(self):
        return self.OPTIONS[
            self.selected_index
        ]

    def draw(
        self,
        screen,
        username,
        account_score,
    ):
        screen.fill(BACKGROUND_COLOR)

        title = self.title_font.render(
            "CYBER SECURITY ADVENTURE",
            True,
            TEXT_COLOR,
        )

        title_rect = title.get_rect(
            center=(
                WIDTH // 2,
                130,
            )
        )

        screen.blit(
            title,
            title_rect,
        )

        subtitle = self.body_font.render(
            t("Дали можеш безбедно да го поминеш денот?"),
            True,
            SUBTEXT_COLOR,
        )

        subtitle_rect = subtitle.get_rect(
            center=(
                WIDTH // 2,
                185,
            )
        )

        screen.blit(
            subtitle,
            subtitle_rect,
        )

        player_text = self.body_font.render(
            t(
                "Играч: {username}",
                username=username,
            ),
            True,
            TEXT_COLOR,
        )

        score_text = self.body_font.render(
            t(
                "Поени на профилот: {account_score}",
                account_score=account_score,
            ),
            True,
            TEXT_COLOR,
        )

        screen.blit(
            player_text,
            (
                WIDTH // 2
                - player_text.get_width() // 2,
                240,
            ),
        )

        screen.blit(
            score_text,
            (
                WIDTH // 2
                - score_text.get_width() // 2,
                275,
            ),
        )

        start_y = 360

        for index, option in enumerate(
            self.OPTIONS
        ):
            selected = (
                index == self.selected_index
            )

            text_color = (
                (245, 205, 110)
                if selected
                else TEXT_COLOR
            )

            option_text = self.body_font.render(
                t(option),
                True,
                text_color,
            )

            option_rect = option_text.get_rect(
                center=(
                    WIDTH // 2,
                    start_y + index * 70,
                )
            )

            if selected:
                pygame.draw.rect(
                    screen,
                    (42, 48, 66),
                    option_rect.inflate(
                        80,
                        24,
                    ),
                    border_radius=10,
                )

                pygame.draw.rect(
                    screen,
                    (90, 170, 230),
                    option_rect.inflate(
                        80,
                        24,
                    ),
                    2,
                    border_radius=10,
                )

            screen.blit(
                option_text,
                option_rect,
            )

        instruction = self.body_font.render(
            t("Користи W/S или стрелките на тастатурата, потоа притисни ENTER"),
            True,
            SUBTEXT_COLOR,
        )

        instruction_rect = (
            instruction.get_rect(
                center=(
                    WIDTH // 2,
                    HEIGHT - 55,
                )
            )
        )

        screen.blit(
            instruction,
            instruction_rect,
        )


class HowToPlayPanel:
    def __init__(
        self,
        title_font,
        body_font,
    ):
        self.title_font = title_font
        self.body_font = body_font

    def draw(self, screen):
        screen.fill(BACKGROUND_COLOR)

        title = self.title_font.render(
            t("HOW TO PLAY"),
            True,
            TEXT_COLOR,
        )

        title_rect = title.get_rect(
            center=(
                WIDTH // 2,
                90,
            )
        )

        screen.blit(
            title,
            title_rect,
        )

        instructions = [
            "Движи се со W, A, S и D.",
            "Притисни E кога си блиску до некој објект или до излез.",
            "Притисни SPACE за да се покаже следниот текст.",
            "Притисни 1 или 2 (или со глувчето) да одговориш на прашањата.",
            "Размисли убаво пред да го заклучиш одговорот.",
            "За да го завршиш денот врати се дома.",
        ]

        y = 175

        for line in instructions:
            rendered = self.body_font.render(
                t(line),
                True,
                TEXT_COLOR,
            )

            screen.blit(
                rendered,
                (
                    WIDTH // 2
                    - rendered.get_width() // 2,
                    y,
                ),
            )

            y += 55

        back_text = self.body_font.render(
            t("Притисни ESCAPE или BACKSPACE за да се вратиш назад"),
            True,
            SUBTEXT_COLOR,
        )

        back_rect = back_text.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT - 60,
            )
        )

        screen.blit(
            back_text,
            back_rect,
        )
