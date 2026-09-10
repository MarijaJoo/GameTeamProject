import pygame

FLAGS = {
    "mk": "assets/flags/mk.png",
    "en": "assets/flags/en.png",
    "tr": "assets/flags/tr.png",
    "sq": "assets/flags/sq.png",
}

from game.localization.localization import (
    LANGUAGES,
    localization,
    t,
)

from game.adventure.settings import (
    BACKGROUND_COLOR,
    SUBTEXT_COLOR,
    TEXT_COLOR,
    WIDTH,
    HEIGHT,
)


class LanguagePanel:
    def __init__(self, title_font, body_font):
        self.title_font = title_font
        self.body_font = body_font

        self.is_open = False

        self.flags = {}


        for language, path in FLAGS.items():
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.smoothscale(image, (48, 30))
            self.flags[language] = image
        self.languages = [
            ("mk", "Македонски"),
            ("en", "English"),
            ("tr", "Türkçe"),
            ("sq", "Shqip"),
        ]

        self.selected_language = localization.get_language()

        self.dropdown_rect = pygame.Rect(
            WIDTH // 2 - 150,
            300,
            300,
            55,
        )

        self.option_rects = []

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP:
                self._move_selection(-1)

            elif event.key == pygame.K_DOWN:
                self._move_selection(1)

            elif event.key in (
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
                pygame.K_SPACE,
            ):
                return self._select_current()

            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button != 1:
                return None

            mouse_pos = event.pos

            if self.dropdown_rect.collidepoint(mouse_pos):
                self.is_open = not self.is_open
                return None

            if self.is_open:
                for index, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected_language = self.languages[index][0]
                        localization.set_language(self.selected_language)
                        self.is_open = False
                        return self.selected_language

        return None

    def _move_selection(self, direction):
        current_index = 0
        for index, (code, _) in enumerate(self.languages):
            if code == self.selected_language:
                current_index = index
                break

        current_index = (current_index + direction) % len(self.languages)
        self.selected_language = self.languages[current_index][0]

    def _select_current(self):
        localization.set_language(self.selected_language)
        self.is_open = False
        return self.selected_language

    def draw(self, screen):
        screen.fill(BACKGROUND_COLOR)

        title = self.title_font.render(
            "CYBER SECURITY ADVENTURE",
            True,
            TEXT_COLOR,
        )
        title_rect = title.get_rect(center=(WIDTH // 2, 130))
        screen.blit(title, title_rect)

        subtitle = self.body_font.render(
            "Choose your language",
            True,
            SUBTEXT_COLOR,
        )
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 220))
        screen.blit(subtitle, subtitle_rect)

        current_name = dict(self.languages)[self.selected_language]

        pygame.draw.rect(
            screen,
            (42, 48, 66),
            self.dropdown_rect,
            border_radius=8,
        )

        pygame.draw.rect(
            screen,
            (90, 170, 230),
            self.dropdown_rect,
            2,
            border_radius=8,
        )

        if self.selected_language in self.flags:
            flag_img = self.flags[self.selected_language]
            flag_rect = flag_img.get_rect(
                midleft=(self.dropdown_rect.x + 20, self.dropdown_rect.centery)
            )
            screen.blit(flag_img, flag_rect)

        selected_text = self.body_font.render(
            current_name,
            True,
            TEXT_COLOR,
        )
        selected_rect = selected_text.get_rect(
            midleft=(self.dropdown_rect.x + 80, self.dropdown_rect.centery)
        )
        screen.blit(selected_text, selected_rect)

        arrow = self.body_font.render("▼", True, TEXT_COLOR)
        screen.blit(
            arrow,
            (self.dropdown_rect.right - 35, self.dropdown_rect.y + 15),
        )

        self.option_rects = []

        if self.is_open:
            option_height = 50

            for index, (code, name) in enumerate(self.languages):
                rect = pygame.Rect(
                    self.dropdown_rect.x,
                    self.dropdown_rect.bottom + index * option_height,
                    self.dropdown_rect.width,
                    option_height,
                )

                self.option_rects.append(rect)

                pygame.draw.rect(screen, (35, 40, 55), rect)
                pygame.draw.rect(screen, (90, 170, 230), rect, 1)

                if code in self.flags:
                    opt_flag = self.flags[code]
                    opt_flag_rect = opt_flag.get_rect(
                        midleft=(rect.x + 20, rect.centery)
                    )
                    screen.blit(opt_flag, opt_flag_rect)

                text = self.body_font.render(name, True, TEXT_COLOR)
                text_rect = text.get_rect(midleft=(rect.x + 80, rect.centery))
                screen.blit(text, text_rect)

        instruction = self.body_font.render(
            "Click the language or use UP/DOWN + ENTER",
            True,
            SUBTEXT_COLOR,
        )
        instruction_rect = instruction.get_rect(
            center=(WIDTH // 2, HEIGHT - 60)
        )
        screen.blit(instruction, instruction_rect)