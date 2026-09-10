import pygame

from game.localization import t


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
from game.arcade.arcade_enemy import (
    VirusEnemy,
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

        self.unlocked_levels = 1
        self.selected_level = 1
        self.current_level = 1
        self.active_knowledge_dot = None
        self.previous_state = None
        self.completed_result = None
        self.software_update_duration = 10000
        self.software_update_until = 0

        self.virus_neutralize_points = 50

        self.arcade_map = ArcadeMap(
            "level_1.txt"
        )

        spawn_x, spawn_y = (
            self.arcade_map.player_spawn
        )
        self.enemies = []

        self.lives = 3

        self.hit_cooldown = 1200
        self.last_hit_time = -self.hit_cooldown

        self.player = ArcadePlayer(
            spawn_x,
            spawn_y,
        )
        self._create_enemies()

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

    def open_level_select(self,unlocked_levels,):
        self.active = True

        self.unlocked_levels = max(1, min(unlocked_levels,4,),)

        self.selected_level = min(
            self.selected_level,
            self.unlocked_levels,
        )

        self.state = "level_select"

    def start_level(self,level_number,):
        if (
                level_number < 1
                or level_number > self.unlocked_levels
        ):
            return

        level_filename = (
            f"level_{level_number}.txt"
        )

        self.arcade_map = ArcadeMap(
            level_filename
        )
        self._create_enemies()

        self.lives = 3
        self.last_hit_time = (
            -self.hit_cooldown
        )
        self.software_update_until = 0

        spawn_x, spawn_y = (
            self.arcade_map.player_spawn
        )

        self.player.reset(spawn_x,spawn_y,)

        self.current_level = level_number

        self.score = 0
        self.active_knowledge_dot = None
        self.previous_state = None
        self.completed_result = None

        self._calculate_map_offset()

        self.state = "playing"

    def close(self):
        self.active = False

    def _reset_level(self):
        self.score = 0
        self.lives = 3
        self.software_update_until = 0
        self.completed_result = None

        self.last_hit_time = (
            -self.hit_cooldown
        )
        self.arcade_map.reset_software_updates()

        for enemy in self.enemies:
            enemy.reset()

        self.arcade_map.reset_collectibles()

        spawn_x, spawn_y = (
            self.arcade_map.player_spawn
        )

        self.player.reset(spawn_x,spawn_y,)
        self.arcade_map.reset_knowledge_dots()
        self.active_knowledge_dot = None
        self.previous_state = None

    def _respawn_after_hit(self):
        spawn_x, spawn_y = (
            self.arcade_map.player_spawn
        )

        self.player.reset(
            spawn_x,
            spawn_y,
        )

        for enemy in self.enemies:
            enemy.reset()

    def _create_enemies(self):
        self.enemies = [
            VirusEnemy(
                spawn_x,
                spawn_y,
            )
            for (
                spawn_x,
                spawn_y,
            ) in self.arcade_map.enemy_spawns
        ]

    def is_software_update_active(self):
        return (
                pygame.time.get_ticks()
                < self.software_update_until
        )

    def _activate_software_update(self):
        self.software_update_until = (
                pygame.time.get_ticks()
                + self.software_update_duration
        )

    def handle_event(self,event,):
        if event.type != pygame.KEYDOWN:
            return False

        if event.key == pygame.K_ESCAPE:
            if self.state == "playing":
                self.completed_result = {
                    "level_number": self.current_level,
                    "score": self.score,
                }
            self.close()
            return True

        if self.state == "level_select":
            if event.key in (
                    pygame.K_a,
                    pygame.K_LEFT,
            ):
                self.selected_level -= 1

                if self.selected_level < 1:
                    self.selected_level = (
                        self.unlocked_levels
                    )

            elif event.key in (
                    pygame.K_d,
                    pygame.K_RIGHT,
            ):
                self.selected_level += 1

                if (
                        self.selected_level
                        > self.unlocked_levels
                ):
                    self.selected_level = 1

            elif event.key in (
                    pygame.K_SPACE,
                    pygame.K_RETURN,
                    pygame.K_KP_ENTER,
            ):
                self.start_level(
                    self.selected_level
                )

            return False

        if self.state == "knowledge_popup":
            if event.key in (
                    pygame.K_SPACE,
                    pygame.K_RETURN,
                    pygame.K_KP_ENTER,
            ):
                self.active_knowledge_dot = None
                self.state = "playing"

            return False

        if self.state == "start":
            if event.key in (
                pygame.K_SPACE,
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
            ):
                self.state = "playing"

            return False
        if self.state == "game_over":
            if event.key in (
                    pygame.K_SPACE,
                    pygame.K_RETURN,
                    pygame.K_KP_ENTER,
            ):
                self._reset_level()
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

    def _check_player_pickups(self):
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

        knowledge_dot = (
            self.arcade_map
            .check_knowledge_collision(
                self.player.rect
            )
        )

        if knowledge_dot is not None:
            self.score += (
                knowledge_dot.POINTS
            )

            self.active_knowledge_dot = (
                knowledge_dot
            )

            self.state = (
                "knowledge_popup"
            )

            return
        software_update = (
            self.arcade_map
            .check_software_update_collision(
                self.player.rect
            )
        )

        if software_update is not None:
            self._activate_software_update()

        if (
                self.arcade_map
                        .all_collectibles_collected()
        ):
            self.completed_result = {
                "level_number": self.current_level,
                "score": self.score,
            }

            self.state = "victory"

    def _check_enemy_collisions(self):
        current_time = pygame.time.get_ticks()

        for enemy in self.enemies:
            if not enemy.active:
                continue

            if not self.player.rect.colliderect(
                    enemy.rect
            ):
                continue

            # SOFTWARE UPDATE ACTIVE:
            # Player neutralizes the Virus.
            if self.is_software_update_active():
                if enemy.neutralize():
                    self.score += (
                        self.virus_neutralize_points
                    )

                return

            # Normal Virus collision.
            if (
                    current_time
                    - self.last_hit_time
                    < self.hit_cooldown
            ):
                return

            self.last_hit_time = current_time

            self.lives -= 1

            if self.lives <= 0:
                self.state = "game_over"
                return

            self._respawn_after_hit()
            return

    def take_completed_result(self):
        result = self.completed_result
        self.completed_result = None

        return result

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

        self.arcade_map.update_knowledge_dots()
        self.arcade_map.update_software_updates()

        for enemy in self.enemies:
            enemy.update(
                self.arcade_map.walls
            )

        self._check_player_pickups()

        # A knowledge popup may have changed
        # the state, so don't process enemies
        # after the game has paused.
        if self.state != "playing":
            return

        self._check_enemy_collisions()

    def draw(self, screen, ):
        screen.fill(
            ARCADE_BACKGROUND_COLOR
        )

        self._draw_background_grid(
            screen
        )

        if self.state == "level_select":
            self._draw_level_select(
                screen
            )

        elif self.state == "start":
            self._draw_start_screen(
                screen
            )

        elif self.state == "playing":
            self._draw_gameplay(
                screen
            )
        elif self.state == "game_over":
            self._draw_gameplay(
                screen
            )

            self._draw_game_over(
                screen
            )

        elif self.state == "victory":
            self._draw_gameplay(
                screen
            )

            self._draw_victory_screen(
                screen
            )
        elif self.state == "knowledge_popup":
            self._draw_gameplay(screen)
            self._draw_knowledge_popup(screen)

    def _draw_background_grid(self, screen, ):
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

    def _draw_level_select(
            self,
            screen,
    ):
        title = self.title_font.render(
        t("БЕЗБЕДНОСЕН БРАНИТЕЛ"),
        True,
            ARCADE_ACCENT_COLOR,
        )

        title_rect = title.get_rect(
            center=(
                self.width // 2,
                100,
            )
        )

        screen.blit(
            title,
            title_rect,
        )

        subtitle = self.body_font.render(
            t("Избери ниво"),
            True,
            ARCADE_TEXT_COLOR,
        )

        subtitle_rect = subtitle.get_rect(
            center=(
                self.width // 2,
                155,
            )
        )

        screen.blit(
            subtitle,
            subtitle_rect,
        )

        card_width = 150
        card_height = 120
        gap = 25

        total_width = (
                card_width * 4
                + gap * 3
        )

        start_x = (
                self.width // 2
                - total_width // 2
        )

        y = 270

        for level_number in range(1, 5,):
            x = (
                    start_x
                    + (level_number - 1)
                    * (card_width + gap)
            )

            rect = pygame.Rect(
                x,
                y,
                card_width,
                card_height,
            )

            unlocked = (
                    level_number
                    <= self.unlocked_levels
            )

            selected = (
                    level_number
                    == self.selected_level
                    and unlocked
            )

            if unlocked:
                background_color = (
                    ARCADE_PANEL_COLOR
                )

                border_color = (
                    ARCADE_ACCENT_COLOR
                    if selected
                    else ARCADE_GRID_COLOR
                )

                text_color = (
                    ARCADE_TEXT_COLOR
                )

            else:
                background_color = (25,30,40,)

                border_color = (60,65,75,)

                text_color = (95,100,110,)

            pygame.draw.rect(screen,background_color,rect,border_radius=12,)

            pygame.draw.rect(screen,border_color,rect,3,border_radius=12,)

            level_text = (
                self.body_font.render(
                    t("НИВО {number}", number=level_number),
                    True,
                    text_color,
                )
            )

            level_rect = (
                level_text.get_rect(
                    center=(
                        rect.centerx,
                        rect.y + 38,
                    )
                )
            )

            screen.blit(level_text,level_rect,)

            if unlocked:
                status = t("ОТКЛУЧЕНО")
            else:
                status = t("ЗАКЛУЧЕНО")

            status_text = (
                self.body_font.render(
                    status,
                    True,
                    text_color,
                )
            )

            status_rect = (
                status_text.get_rect(
                    center=(
                        rect.centerx,
                        rect.y + 82,
                    )
                )
            )

            screen.blit(status_text,status_rect,)

        controls = self.body_font.render(
            (
                t("A/D или стрелки: избор    SPACE: играј    ESC: назад")
            ),
            True,
            ARCADE_SUBTEXT_COLOR,
        )

        controls_rect = (
            controls.get_rect(
                center=(
                    self.width // 2,
                    self.height - 70,
                )
            )
        )

        screen.blit(controls,controls_rect,)

    def _draw_start_screen(self, screen,):
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
            t("БЕЗБЕДНОСЕН БРАНИТЕЛ"),
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

            t("Собери ги сите точки на знаење во мрежата."),
            t("Движи се со WASD или стрелките."),
            t("Избегнувај ги сајбер заканите."),
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

            screen.blit(rendered,rendered_rect,)

            y += 48

        start_text = self.body_font.render(
            t("Притисни SPACE за да започнеш"),
            True,
            ARCADE_ACCENT_COLOR,
        )

        start_rect = start_text.get_rect(
            center=(
                self.width // 2,
                panel.bottom - 100,
            )
        )

        screen.blit(start_text,start_rect,)

        exit_text = self.body_font.render(
            t("Притисни ESC за да се вратиш Дома"),
            True,
            ARCADE_SUBTEXT_COLOR,
        )

        exit_rect = exit_text.get_rect(
            center=(
                self.width // 2,
                panel.bottom - 50,
            )
        )

        screen.blit(exit_text,exit_rect,)

    def _draw_gameplay(self,screen,):
        self.arcade_map.draw(
            screen,
            self.map_offset_x,
            self.map_offset_y,
        )

        vulnerable = (
            self.is_software_update_active()
        )

        for enemy in self.enemies:
            enemy.draw(
                screen,
                self.map_offset_x,
                self.map_offset_y,
                vulnerable=vulnerable,
            )

        self.player.draw(
            screen,
            self.map_offset_x,
            self.map_offset_y,
        )

        self._draw_gameplay_hud(screen)

    def _draw_gameplay_hud(self,screen,):
        score_text = self.body_font.render(
            t("Поени: {score}", score=self.score),
            True,
            ARCADE_TEXT_COLOR,
        )
        lives_text = self.body_font.render(
            t("Животи: {lives}", lives=self.lives),
        True,
            ARCADE_TEXT_COLOR,
        )
        screen.blit(lives_text,(30, 55),
)
        remaining = (
            self.arcade_map
            .get_remaining_collectibles()
        )

        remaining_text = (
            self.body_font.render(
                (
                    t(
                        "Преостанати модули: {remaining}",
                        remaining=remaining,
                    )
                ),
                True,
                ARCADE_TEXT_COLOR,
            )
        )
        remaining_knowledge = sum(
            not knowledge_dot.collected
            for knowledge_dot in self.arcade_map.knowledge_dots
        )
        knowledge_text = self.body_font.render(
            t(
                "Знаење: {number}",
                number=remaining_knowledge,
            ),
            True,
            ARCADE_TEXT_COLOR,
        )
        screen.blit(
            knowledge_text,
            (30, 85),
        )

        exit_text = self.body_font.render(
            t("ESC: Врати се Дома"),
            True,
            ARCADE_SUBTEXT_COLOR,
        )

        screen.blit(score_text,(30, 25),)

        remaining_rect = (
            remaining_text.get_rect(
                center=(self.width // 2,40,)
            )
        )

        screen.blit(remaining_text, remaining_rect,)

        exit_rect = exit_text.get_rect(
            topright=(self.width - 30, 25,)
        )

        screen.blit(exit_text,exit_rect,)

        if self.is_software_update_active():
            remaining_ms = (
                    self.software_update_until
                    - pygame.time.get_ticks()
            )

            remaining_seconds = max(
                0,
                remaining_ms / 1000,
            )

            update_text = self.body_font.render(
                (t(
                        "БЕЗБЕДНОСНО АЖУРИРАЊЕ: {seconds:.1f}s",
                        seconds=remaining_seconds,
                    )
                ),
                True,
                (100, 195, 255),
            )

            update_rect = update_text.get_rect(
                center=(
                    self.width // 2,
                    70,
                )
            )

            screen.blit(
                update_text,
                update_rect,
            )

    def _draw_game_over(
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
            (5, 10, 20, 215)
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
            (220, 70, 85),
            panel,
            3,
            border_radius=16,
        )

        title = self.title_font.render(
            t("КРАЈ НА ИГРАТА"),
            True,
            (220, 70, 85),
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

        score_text = self.body_font.render(
            t(
                "Резултат: {score}",
                score=self.score,
            ),
            True,
            ARCADE_TEXT_COLOR,
        )

        score_rect = score_text.get_rect(
            center=(
                self.width // 2,
                panel.y + 125,
            )
        )

        screen.blit(
            score_text,
            score_rect,
        )

        controls = self.body_font.render(
            t("SPACE: Обиди се повторно    ESC: Назад"),
            True,
            ARCADE_SUBTEXT_COLOR,
        )

        controls_rect = controls.get_rect(
            center=(
                self.width // 2,
                panel.bottom - 50,
            )
        )

        screen.blit(
            controls,
            controls_rect,
        )

    def _draw_victory_screen(self,screen,):
        overlay = pygame.Surface(
            (self.width, self.height,),
            pygame.SRCALPHA,
        )

        overlay.fill((5, 10, 20, 205))

        screen.blit(overlay,(0, 0),)

        panel = pygame.Rect(
            205,
            165,
            self.width - 410,
            self.height - 330,
        )

        pygame.draw.rect(screen, ARCADE_PANEL_COLOR, panel, border_radius=16,)

        pygame.draw.rect(screen,ARCADE_ACCENT_COLOR,panel,3,border_radius=16,)

        title = self.title_font.render(t("МРЕЖАТА Е ОБЕЗБЕДЕНА!"),True,ARCADE_ACCENT_COLOR,)

        title_rect = title.get_rect(
            center=(
                self.width // 2,
                panel.y + 65,
            )
        )

        screen.blit(title,title_rect,)

        score = self.body_font.render(
            t(
                "Финални поени: {score}",
                score=self.score,
            ),
            True,
            ARCADE_TEXT_COLOR,
        )

        score_rect = score.get_rect(
            center=(
                self.width // 2,
                panel.y + 125,
            )
        )

        screen.blit(score,score_rect,)

        controls = self.body_font.render(
            t("R: Играј повторно    SPACE: Врати се Дома"),
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

        screen.blit(controls,controls_rect,)

    def _wrap_text(self,text,maximum_width,):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = (
                f"{current_line} {word}".strip()
            )

            if (
                    self.body_font.size(
                        test_line
                    )[0]
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

    def _draw_knowledge_popup(self,screen,):
        if self.active_knowledge_dot is None:
            return

        overlay = pygame.Surface(
            (self.width,self.height,),
            pygame.SRCALPHA,
        )

        overlay.fill((5, 10, 20, 210))

        screen.blit(overlay,(0, 0),)

        panel = pygame.Rect(
            175,
            135,
            self.width - 350,
            self.height - 270,
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
            t(self.active_knowledge_dot.name),
            True,
            ARCADE_ACCENT_COLOR,
        )

        title_rect = title.get_rect(
            center=(
                self.width // 2,
                panel.y + 65,
            )
        )

        screen.blit(title,title_rect,)

        lines = self._wrap_text(
            t(self.active_knowledge_dot.description),
            panel.width - 90,
        )

        y = panel.y + 135

        for line in lines:
            rendered = self.body_font.render(
                line,
                True,
                ARCADE_TEXT_COLOR,
            )

            rendered_rect = rendered.get_rect( center=(self.width // 2, y,) )

            screen.blit(rendered,rendered_rect,)

            y += 36

        continue_text = self.body_font.render(
            t("Притисни SPACE за да продолжиш"),
            True,
            ARCADE_SUBTEXT_COLOR,
        )

        continue_rect = (
            continue_text.get_rect(
                center=(
                    self.width // 2,
                    panel.bottom - 50,
                )
            )
        )

        screen.blit(continue_text,continue_rect,)