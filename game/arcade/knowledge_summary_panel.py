import pygame

from game.arcade.knowledge_topics import KNOWLEDGE_TOPICS
from game.arcade.arcade_settings import (
    ARCADE_ACCENT_COLOR,
    ARCADE_PANEL_COLOR,
    ARCADE_SUBTEXT_COLOR,
    ARCADE_TEXT_COLOR,
    ARCADE_GRID_COLOR,
)
from game.localization import t


class KnowledgeSummaryPanel:
    # 8 items = 2 columns x 4 rows
    # This gives every knowledge item enough room
    # for its complete description.
    ITEMS_PER_PAGE = 8

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.current_page = 0

        self.overlay_color = (5, 10, 20, 225)

        self.panel = pygame.Rect(
            35,
            25,
            width - 70,
            height - 50,
        )

    def open(self):
        self.current_page = 0

    def close(self):
        self.current_page = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key in (
                pygame.K_ESCAPE,
                pygame.K_SPACE,
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
            ):
                return "close"

            if event.key in (
                pygame.K_RIGHT,
                pygame.K_d,
                pygame.K_PAGEDOWN,
            ):
                self.next_page()
                return True

            if event.key in (
                pygame.K_LEFT,
                pygame.K_a,
                pygame.K_PAGEUP,
            ):
                self.previous_page()
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:
                return "close"

        return False

    def next_page(self):
        total_pages = self.get_total_pages()

        if total_pages <= 1:
            return

        self.current_page += 1

        if self.current_page >= total_pages:
            self.current_page = 0

    def previous_page(self):
        total_pages = self.get_total_pages()

        if total_pages <= 1:
            return

        self.current_page -= 1

        if self.current_page < 0:
            self.current_page = total_pages - 1

    def get_total_pages(self):
        collected_count = len(
            self._get_collected_topics()
        )

        if collected_count == 0:
            return 1

        return (
            collected_count + self.ITEMS_PER_PAGE - 1
        ) // self.ITEMS_PER_PAGE

    def _get_collected_topics(self):
        return getattr(
            self,
            "_collected_topics",
            [],
        )

    def draw(self, screen, collected_topics):

        self._collected_topics = (
            collected_topics or []
        )

        total_pages = self.get_total_pages()

        if self.current_page >= total_pages:
            self.current_page = max(
                0,
                total_pages - 1,
            )

        # =================================================
        # DARK OVERLAY
        # =================================================

        overlay = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA,
        )

        overlay.fill(self.overlay_color)

        screen.blit(
            overlay,
            (0, 0),
        )

        # =================================================
        # MAIN PANEL
        # =================================================

        pygame.draw.rect(
            screen,
            ARCADE_PANEL_COLOR,
            self.panel,
            border_radius=18,
        )

        pygame.draw.rect(
            screen,
            ARCADE_ACCENT_COLOR,
            self.panel,
            3,
            border_radius=18,
        )

        # =================================================
        # TITLE
        # =================================================

        title_font = pygame.font.Font(
            None,
            30,
        )

        title = title_font.render(
            t("РЕЗИМЕ НА ЗНАЕЊЕТО"),
            True,
            ARCADE_ACCENT_COLOR,
        )

        title_rect = title.get_rect(
            center=(
                self.panel.centerx,
                self.panel.y + 28,
            ),
        )

        screen.blit(
            title,
            title_rect,
        )

        # =================================================
        # EMPTY STATE
        # =================================================

        if not self._collected_topics:

            empty_font = pygame.font.Font(
                None,
                27,
            )

            empty_text = empty_font.render(
                t(
                    "Сè уште немаш собрано знаење."
                ),
                True,
                ARCADE_TEXT_COLOR,
            )

            empty_rect = empty_text.get_rect(
                center=self.panel.center,
            )

            screen.blit(
                empty_text,
                empty_rect,
            )

            self._draw_footer(
                screen,
                total_pages,
            )

            return

        # =================================================
        # PAGE TEXT
        # =================================================

        page_font = pygame.font.Font(
            None,
            22,
        )

        page_text = page_font.render(
            t(
                "Страница {current}/{total}",
                current=self.current_page + 1,
                total=total_pages,
            ),
            True,
            ARCADE_SUBTEXT_COLOR,
        )

        page_rect = page_text.get_rect(
            center=(
                self.panel.centerx,
                self.panel.y + 55,
            ),
        )

        screen.blit(
            page_text,
            page_rect,
        )

        # =================================================
        # PAGE ITEMS
        # =================================================

        start_index = (
            self.current_page
            * self.ITEMS_PER_PAGE
        )

        end_index = min(
            start_index + self.ITEMS_PER_PAGE,
            len(self._collected_topics),
        )

        page_items = self._collected_topics[
            start_index:end_index
        ]

        # =================================================
        # TWO COLUMNS
        # =================================================

        column_width = (
            self.panel.width - 75
        ) // 2

        left_x = self.panel.x + 25

        right_x = (
            self.panel.x
            + 25
            + column_width
        )

        # 4 rows with taller cards.
        top_y = self.panel.y + 78

        row_height = 125

        for index, topic in enumerate(
            page_items
        ):

            column = index % 2
            row = index // 2

            if column == 0:
                x = left_x
            else:
                x = right_x

            y = top_y + row * row_height

            self._draw_topic(
                screen,
                topic,
                x,
                y,
                column_width - 10,
            )

        # =================================================
        # FOOTER
        # =================================================

        self._draw_footer(
            screen,
            total_pages,
        )

    def _draw_topic(
        self,
        screen,
        topic,
        x,
        y,
        width,
    ):

        name = topic.get(
            "name",
            "",
        )

        description = topic.get(
            "description",
            "",
        )

        name = t(name)
        description = t(description)

        # =================================================
        # CARD
        # =================================================

        item_height = 112

        item_rect = pygame.Rect(
            x,
            y,
            width,
            item_height,
        )

        pygame.draw.rect(
            screen,
            (30, 40, 58),
            item_rect,
            border_radius=10,
        )

        pygame.draw.rect(
            screen,
            ARCADE_GRID_COLOR,
            item_rect,
            1,
            border_radius=10,
        )

        # =================================================
        # TOPIC NAME
        # =================================================

        font_name = pygame.font.Font(
            None,
            23,
        )

        name_surface = font_name.render(
            name,
            True,
            ARCADE_ACCENT_COLOR,
        )

        # Scale the name down if necessary.
        while (
            name_surface.get_width()
            > width - 24
            and font_name.get_height() > 16
        ):

            font_name = pygame.font.Font(
                None,
                font_name.get_height() - 1,
            )

            name_surface = font_name.render(
                name,
                True,
                ARCADE_ACCENT_COLOR,
            )

        screen.blit(
            name_surface,
            (
                x + 12,
                y + 7,
            ),
        )

        # =================================================
        # FULL DESCRIPTION
        # =================================================

        font_description = pygame.font.Font(
            None,
            17,
        )

        lines = self._wrap_text(
            description,
            font_description,
            width - 24,
        )

        description_y = y + 33

        # Draw EVERY wrapped line.
        for line in lines:

            description_surface = (
                font_description.render(
                    line,
                    True,
                    ARCADE_TEXT_COLOR,
                )
            )

            screen.blit(
                description_surface,
                (
                    x + 12,
                    description_y,
                ),
            )

            description_y += 18

            # Safety: never draw outside the card.
            if (
                description_y
                >= y + item_height - 5
            ):
                break

    def _wrap_text(
        self,
        text,
        font,
        maximum_width,
    ):

        words = text.split()

        lines = []
        current_line = ""

        for word in words:

            test_line = (
                f"{current_line} {word}".strip()
            )

            if (
                font.size(test_line)[0]
                <= maximum_width
            ):

                current_line = test_line

            else:

                if current_line:
                    lines.append(
                        current_line
                    )

                current_line = word

        if current_line:
            lines.append(
                current_line
            )

        return lines

    def _draw_footer(
        self,
        screen,
        total_pages,
    ):

        font = pygame.font.Font(
            None,
            19,
        )

        if total_pages > 1:

            controls = t(
                "Лево/десно: страница    SPACE/клик: назад"
            )

        else:

            controls = t(
                "SPACE/клик: назад"
            )

        text = font.render(
            controls,
            True,
            ARCADE_SUBTEXT_COLOR,
        )

        rect = text.get_rect(
            center=(
                self.panel.centerx,
                self.panel.bottom - 18,
            ),
        )

        screen.blit(
            text,
            rect,
        )