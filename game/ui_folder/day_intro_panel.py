import pygame

from game.adventure.settings import (
    HEIGHT,
    SUBTEXT_COLOR,
    TEXT_COLOR,
    WIDTH,
)
from game.localization import t


class DayIntroPanel:

    def __init__(self, title_font, body_font):
        self.title_font = title_font
        self.body_font = body_font
        self.page = 0

        self.pages = [
            "Започна како и секој друг ден. Си ја вршеше вообичаената рутина кога нешто чудно почна да се случува околу тебе.",
             "Сомнителни пораки, опасни линкови, лажни веб-страници, непознати уреди... сајбер заканите беа насекаде. И колку повеќе гледаше, толку повеќе сфаќаше дека дури и обичните работи можат да те доведат во ризик.",
            "Сега е на тебе да се заштитиш. Истражи ја секоја соба, соочи се со различни закани за сајбер-безбедноста и искористи го наученото за да останеш безбеден. Подготвен ли си?",
             "Истражи ги сите четири соби, заврши ги дијалозите и предизвиците и собирај знаење. Колку повеќе учиш, толку подобро ќе бидеш подготвен да се одбраниш од сајбер закани.",
        ]

    def next_page(self):
        self.page += 1
        if self.page >= len(self.pages):
            return True
        return False

    def draw(self, screen):
        # Dark transparent overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        # Popup
        panel = pygame.Rect(140, 150, WIDTH - 280, 360)

        pygame.draw.rect(screen, (42, 48, 66), panel, border_radius=16)
        pygame.draw.rect(
            screen, (90, 170, 230), panel, 3, border_radius=16
        )

        # Title
        # title = self.title_font.render(t(""), True, TEXT_COLOR)
        # title_rect = title.get_rect(center=(WIDTH // 2, panel.y + 55))
        # screen.blit(title, title_rect)

        # Current Page Message
        current_text = self.pages[self.page]
        self._draw_wrapped_text(
            screen,
            t(current_text),
            panel.x + 40,
            panel.y + 85,
            panel.width - 80,
        )

        page_indicator = f"({self.page + 1}/{len(self.pages)}) "
        translated_instruction = t("Притисни SPACE за да продолжиш")
        full_instruction = f"{page_indicator}{translated_instruction}"

        instruction = self.body_font.render(full_instruction, True, SUBTEXT_COLOR)
        instruction_rect = instruction.get_rect(
            center=(WIDTH // 2, panel.bottom - 45)
        )
        screen.blit(instruction, instruction_rect)

    def _draw_wrapped_text(self, screen, text, x, y, max_width):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = (
                word if not current_line else current_line + " " + word
            )
            if self.body_font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        line_height = self.body_font.get_height() + 3
        for line in lines:
            rendered = self.body_font.render(line, True, TEXT_COLOR)
            screen.blit(rendered, (x, y))
            y += line_height