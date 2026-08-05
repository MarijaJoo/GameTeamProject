import pygame

from game.arcade.arcade_map import (
    ArcadeMap,
)
from game.arcade.arcade_player import (
    ArcadePlayer,
)
from game.arcade.arcade_settings import (
    ARCADE_ACCENT_COLOR,
    ARCADE_BACKGROUND_COLOR,
    ARCADE_GRID_COLOR,
    ARCADE_PANEL_COLOR,
    ARCADE_SUBTEXT_COLOR,
    ARCADE_TEXT_COLOR,
    COLLECTIBLE_POINTS,
)


class ArcadeGame:
    def __init__(
        self,
        width,
        height,
        title_font,
        body_font,
    ):
        self.width = width
        self.height = height

        self.title_font = title_font
        self.body_font = body_font

        self.active = False
        self.state = "start"

        self.score = 0

        self.arcade_map = ArcadeMap(
            "level_1.txt"
        )

        spawn_x, spawn_y = (
            self.arcade_map.player_spawn
        )

        self.player = ArcadePlayer(
            spawn_x,
            spawn_y,
        )

        self.map_offset_x = 0
        self.map_offset_y = 0

        self._calculate_map_offset()

    def _calculate_map_offset(self):
        self.map_offset_x = (
            self.width
            - self.arcade_map.width
        ) // 2

        # Leave room for the HUD.
        self.map_offset_y = max(
            85,
            (
                self.height
                - self.arcade_map.height
            ) // 2
            + 25,
        )

    def start(self):
        self.active = True
        self.state = "start"

        self._reset_level()

    def close(self):
        self.active = False

    def _reset_level(self):
        self.score = 0

        self.arcade_map.reset_collectibles()

        spawn_x, spawn_y = (
            self.arcade_map.player_spawn
        )

        self.player.reset(
            spawn_x,
            spawn_y,
        )

    def handle_event(
        self,
        event,
    ):
        if event.type != pygame.KEYDOWN:
            return False

        if event.key == pygame.K_ESCAPE:
            self.close()
            return True

        if self.state == "start":
            if event.key in (
                pygame.K_SPACE,
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
            ):
                self.state = "playing"

            return False

        if self.state == "victory":
            if event.key == pygame.K_r:
                self._reset_level()
                self.state = "playing"

            elif event.key in (
                pygame.K_SPACE,
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
            ):
                self.close()
                return True

        return False

    def update(self):
        if (
            not self.active
            or self.state != "playing"
        ):
            return

        keys = pygame.key.get_pressed()

        self.player.handle_input(
            keys,
            self.arcade_map.walls,
        )

        collected_count = (
            self.arcade_map
            .check_collectible_collision(
                self.player.rect
            )
        )

        if collected_count > 0:
            self.score += (
                collected_count
                * COLLECTIBLE_POINTS
            )

        if (
            self.arcade_map
            .all_collectibles_collected()
        ):
            self.state = "victory"

    def draw(
        self,
        screen,
    ):
        screen.fill(
            ARCADE_BACKGROUND_COLOR
        )

        self._draw_background_grid(
            screen
        )

        if self.state == "start":
            self._draw_start_screen(
                screen
            )

        elif self.state == "playing":
            self._draw_gameplay(
                screen
            )

        elif self.state == "victory":
            self._draw_gameplay(
                screen
            )

            self._draw_victory_screen(
                screen
            )

    def _draw_background_grid(
        self,
        screen,
    ):
        grid_size = 40

        for x in range(
            0,
            self.width,
            grid_size,
        ):
            pygame.draw.line(
                screen,
                ARCADE_GRID_COLOR,
                (x, 0),
                (x, self.height),
                1,
            )

        for y in range(
            0,
            self.height,
            grid_size,
        ):
            pygame.draw.line(
                screen,
                ARCADE_GRID_COLOR,
                (0, y),
                (self.width, y),
                1,
            )

    def _draw_start_screen(
        self,
        screen,
    ):
        panel = pygame.Rect(
            150,
            110,
            self.width - 300,
            self.height - 220,
        )

        pygame.draw.rect(
            screen,
            ARCADE_PANEL_COLOR,
            panel,
            border_radius=18,
        )

        pygame.draw.rect(
            screen,
            ARCADE_ACCENT_COLOR,
            panel,
            3,
            border_radius=18,
        )

        title = self.title_font.render(
            "SECURITY DEFENDER",
            True,
            ARCADE_ACCENT_COLOR,
        )

        title_rect = title.get_rect(
            center=(
                self.width // 2,
                panel.y + 70,
            )
        )

        screen.blit(
            title,
            title_rect,
        )

        instructions = [
            (
                "Collect every knowledge point "
                "inside the network."
            ),
            "Move with WASD or arrow keys.",
            "Avoiding cyber threats will be added next.",
        ]

        y = panel.y + 145

        for instruction in instructions:
            rendered = (
                self.body_font.render(
                    instruction,
                    True,
                    ARCADE_TEXT_COLOR,
                )
            )

            rendered_rect = (
                rendered.get_rect(
                    center=(
                        self.width // 2,
                        y,
                    )
                )
            )

            screen.blit(
                rendered,
                rendered_rect,
            )

            y += 48

        start_text = self.body_font.render(
            "Press SPACE to start",
            True,
            ARCADE_ACCENT_COLOR,
        )

        start_rect = start_text.get_rect(
            center=(
                self.width // 2,
                panel.bottom - 100,
            )
        )

        screen.blit(
            start_text,
            start_rect,
        )

        exit_text = self.body_font.render(
            "Press ESC to return Home",
            True,
            ARCADE_SUBTEXT_COLOR,
        )

        exit_rect = exit_text.get_rect(
            center=(
                self.width // 2,
                panel.bottom - 50,
            )
        )

        screen.blit(
            exit_text,
            exit_rect,
        )

    def _draw_gameplay(
        self,
        screen,
    ):
        self.arcade_map.draw(
            screen,
            self.map_offset_x,
            self.map_offset_y,
        )

        self.player.draw(
            screen,
            self.map_offset_x,
            self.map_offset_y,
        )

        self._draw_gameplay_hud(
            screen
        )

    def _draw_gameplay_hud(
        self,
        screen,
    ):
        score_text = self.body_font.render(
            f"Score: {self.score}",
            True,
            ARCADE_TEXT_COLOR,
        )

        remaining = (
            self.arcade_map
            .get_remaining_collectibles()
        )

        remaining_text = (
            self.body_font.render(
                (
                    "Modules remaining: "
                    f"{remaining}"
                ),
                True,
                ARCADE_TEXT_COLOR,
            )
        )

        exit_text = self.body_font.render(
            "ESC: Return Home",
            True,
            ARCADE_SUBTEXT_COLOR,
        )

        screen.blit(
            score_text,
            (30, 25),
        )

        remaining_rect = (
            remaining_text.get_rect(
                center=(
                    self.width // 2,
                    40,
                )
            )
        )

        screen.blit(
            remaining_text,
            remaining_rect,
        )

        exit_rect = exit_text.get_rect(
            topright=(
                self.width - 30,
                25,
            )
        )

        screen.blit(
            exit_text,
            exit_rect,
        )

    def _draw_victory_screen(
        self,
        screen,
    ):
        overlay = pygame.Surface(
            (
                self.width,
                self.height,
            ),
            pygame.SRCALPHA,
        )

        overlay.fill(
            (5, 10, 20, 205)
        )

        screen.blit(
            overlay,
            (0, 0),
        )

        panel = pygame.Rect(
            205,
            165,
            self.width - 410,
            self.height - 330,
        )

        pygame.draw.rect(
            screen,
            ARCADE_PANEL_COLOR,
            panel,
            border_radius=16,
        )

        pygame.draw.rect(
            screen,
            ARCADE_ACCENT_COLOR,
            panel,
            3,
            border_radius=16,
        )

        title = self.title_font.render(
            "NETWORK SECURED!",
            True,
            ARCADE_ACCENT_COLOR,
        )

        title_rect = title.get_rect(
            center=(
                self.width // 2,
                panel.y + 65,
            )
        )

        screen.blit(
            title,
            title_rect,
        )

        score = self.body_font.render(
            f"Final arcade score: {self.score}",
            True,
            ARCADE_TEXT_COLOR,
        )

        score_rect = score.get_rect(
            center=(
                self.width // 2,
                panel.y + 125,
            )
        )

        screen.blit(
            score,
            score_rect,
        )

        controls = self.body_font.render(
            "R: Replay    SPACE: Return Home",
            True,
            ARCADE_SUBTEXT_COLOR,
        )

        controls_rect = (
            controls.get_rect(
                center=(
                    self.width // 2,
                    panel.bottom - 50,
                )
            )
        )

        screen.blit(
            controls,
            controls_rect,
        )