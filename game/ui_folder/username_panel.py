
import pygame

from game.adventure.settings import (
    BACKGROUND_COLOR,
    HEIGHT,
    SUBTEXT_COLOR,
    TEXT_COLOR,
    WIDTH,
)


class UsernamePanel:
    MAX_LENGTH = 20

    def __init__(
        self,
        title_font,
        body_font,
    ):
        self.title_font = title_font
        self.body_font = body_font

        self.username = ""
        self.error_message = ""

    def handle_key(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.username = self.username[:-1]
            self.error_message = ""
            return None

        if event.key in (
            pygame.K_RETURN,
            pygame.K_KP_ENTER,
        ):
            cleaned_username = self.username.strip()

            if not cleaned_username:
                self.error_message = (
                    "Внесете го вашето корисничко име"
                )
                return None

            return cleaned_username

        if (
            event.unicode
            and event.unicode.isprintable()
            and len(self.username) < self.MAX_LENGTH
        ):
            self.username += event.unicode
            self.error_message = ""

        return None

    def reset(self):
        self.username = ""
        self.error_message = ""

    def draw(self, screen):
        screen.fill(BACKGROUND_COLOR)

        title = self.title_font.render(
            "CYBER SECURITY ADVENTURE",
            True,
            TEXT_COLOR,
        )

        title_rect = title.get_rect(
            center=(
                WIDTH // 2,
                140,
            )
        )

        screen.blit(
            title,
            title_rect,
        )

        prompt = self.body_font.render(
            "Внесете го вашето корисничко име",
            True,
            SUBTEXT_COLOR,
        )

        prompt_rect = prompt.get_rect(
            center=(
                WIDTH // 2,
                255,
            )
        )

        screen.blit(
            prompt,
            prompt_rect,
        )

        input_box = pygame.Rect(
            WIDTH // 2 - 220,
            310,
            440,
            65,
        )

        pygame.draw.rect(
            screen,
            (42, 48, 66),
            input_box,
            border_radius=10,
        )

        pygame.draw.rect(
            screen,
            (90, 170, 230),
            input_box,
            3,
            border_radius=10,
        )

        visible_username = (
            self.username
            if self.username
            else "Type here..."
        )

        username_color = (
            TEXT_COLOR
            if self.username
            else SUBTEXT_COLOR
        )

        username_text = self.body_font.render(
            visible_username,
            True,
            username_color,
        )

        screen.blit(
            username_text,
            (
                input_box.x + 18,
                input_box.centery
                - username_text.get_height() // 2,
            ),
        )

        if (
            pygame.time.get_ticks() // 500
        ) % 2 == 0:
            cursor_x = (
                input_box.x
                + 18
                + username_text.get_width()
                + 3
            )

            pygame.draw.line(
                screen,
                TEXT_COLOR,
                (
                    cursor_x,
                    input_box.y + 16,
                ),
                (
                    cursor_x,
                    input_box.bottom - 16,
                ),
                2,
            )

        if self.error_message:
            error_text = self.body_font.render(
                self.error_message,
                True,
                (220, 90, 100),
            )

            error_rect = error_text.get_rect(
                center=(
                    WIDTH // 2,
                    415,
                )
            )

            screen.blit(
                error_text,
                error_rect,
            )

        instruction = self.body_font.render(
            "Притисни ENTER за да продолжиш",
            True,
            SUBTEXT_COLOR,
        )

        instruction_rect = instruction.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT - 90,
            )
        )

        screen.blit(
            instruction,
            instruction_rect,
        )
