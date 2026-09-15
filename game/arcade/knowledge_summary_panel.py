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
    ITEMS_PER_PAGE = 16

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.current_page = 0

        self.overlay_color = (5, 10, 20, 225)

        # Larger window so the knowledge screen has more space.
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
        """
        Returns:
            True      -> event was handled
            False     -> event was not handled
            "close"   -> close the knowledge window
        """

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
        """
        This panel receives the topics that the player
        has actually collected.
        """

        return getattr(
            self,
            "_collected_topics",
            [],
        )

    def draw(self, screen, collected_topics):
        """
        Draw the knowledge summary.

        collected_topics should be a list of topic
        dictionaries from KNOWLEDGE_TOPICS.
        """

        self._collected_topics = collected_topics or []

        total_pages = self.get_total_pages()

        # Safety: don't allow an invalid page.
        if self.current_page >= total_pages:
            self.current_page = max(
                0,
                total_pages - 1,
            )

        # -------------------------------------------------
        # DARK OVERLAY
        # -------------------------------------------------

        overlay = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA,
        )

        overlay.fill(self.overlay_color)

        screen.blit(
            overlay,
            (0, 0),
        )

        # -------------------------------------------------
        # MAIN PANEL
        # -------------------------------------------------

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

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

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
                self.panel.y + 30,
            )
        )

        screen.blit(
            title,
            title_rect,
        )

        # -------------------------------------------------
        # EMPTY STATE
        # -------------------------------------------------

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

        # -------------------------------------------------
        # PAGE TEXT
        # -------------------------------------------------

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
                self.panel.y + 57,
            )
        )

        screen.blit(
            page_text,
            page_rect,
        )

        # -------------------------------------------------
        # CURRENT PAGE ITEMS
        # -------------------------------------------------

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

        # -------------------------------------------------
        # TWO COLUMNS
        # -------------------------------------------------

        column_width = (
            self.panel.width - 70
        ) // 2

        left_x = self.panel.x + 25

        right_x = (
            self.panel.x
            + 25
            + column_width
        )

        # Start the cards higher because the title
        # and page text are now smaller.
        top_y = self.panel.y + 82

        # Slightly smaller spacing allows all
        # 16 items to fit comfortably.
        row_height = 59

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

        # -------------------------------------------------
        # FOOTER
        # -------------------------------------------------

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
        # -------------------------------------------------
        # TOPIC DATA
        # -------------------------------------------------

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

        # -------------------------------------------------
        # ITEM BACKGROUND
        # -------------------------------------------------

        item_rect = pygame.Rect(
            x,
            y,
            width,
            51,
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

        # -------------------------------------------------
        # TOPIC NAME
        # -------------------------------------------------

        font_name = pygame.font.Font(
            None,
            23,
        )

        name_surface = font_name.render(
            name,
            True,
            ARCADE_ACCENT_COLOR,
        )

        # Prevent very long names from leaving
        # the card.
        if name_surface.get_width() > width - 24:
            while (
                font_name.get_height() > 15
                and name_surface.get_width()
                > width - 24
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
                y + 6,
            ),
        )

        # -------------------------------------------------
        # DESCRIPTION
        # -------------------------------------------------

        font_description = pygame.font.Font(
            None,
            17,
        )

        lines = self._wrap_text(
            description,
            font_description,
            width - 24,
        )

        # Keep the grid compact.
        if lines:
            description_surface = (
                font_description.render(
                    lines[0],
                    True,
                    ARCADE_TEXT_COLOR,
                )
            )

            screen.blit(
                description_surface,
                (
                    x + 12,
                    y + 29,
                ),
            )

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
        # Smaller footer so it never crowds
        # the knowledge cards.
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
            )
        )

        screen.blit(
            text,
            rect,
        )