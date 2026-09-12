import pygame

from game.adventure.settings import (
    BACKGROUND_COLOR,
    HEIGHT,
    WIDTH,
)


class GameRenderer:
    def draw(self, game):
        """
        Draws the current game state.

        The game object provides the current world, player,
        panels, fonts, score, and state.
        """
        if game.game_state == "language":
            game.language_panel.draw(
                game.screen
            )
            pygame.display.flip()

            return

        if game.game_state == "username":
            game.username_panel.draw(
                game.screen
            )
            pygame.display.flip()
            return

        if game.game_state == "menu":
            game.menu_panel.draw(
                game.screen,
                game.username,
                game.score,
            )
            pygame.display.flip()
            return

        if game.game_state == "how_to_play":
            game.how_to_play_panel.draw(
                game.screen
            )
            pygame.display.flip()
            return

        if game.game_state == "arcade":
            game.arcade_game.draw(
                game.screen
            )

            pygame.display.flip()
            return

        game.screen.fill(
            BACKGROUND_COLOR
        )

        game.world.current_location.draw(
            game.screen,
            game.body_font,
        )

        game.player.draw(
            game.screen
        )

        game.hud.draw(
            game.screen,
            game.username,
            game.total_score,
            game.api.online,
            game.world.current_location.name,
        )
        collected, required = (
            game.get_knowledge_progress()
        )

        game.hud.draw_knowledge_progress(
            game.screen,
            collected,
            required,
        )

        if (
            game.nearby_object is not None
            and game.game_state == "exploring"
        ):
            game.hud.draw_interaction_prompt(
                game.screen,
                game.nearby_object,
            )

        self._draw_notice(game)
        self._draw_active_panel(game)

        pygame.display.flip()

    @staticmethod
    def _draw_notice(game):
        current_time = pygame.time.get_ticks()

        if (
            game.notice_message
            and current_time < game.notice_until
        ):
            notice = game.body_font.render(
                game.notice_message,
                True,
                (245, 205, 110),
            )

            notice_rect = notice.get_rect(
                center=(
                    WIDTH // 2,
                    HEIGHT - 75,
                )
            )

            pygame.draw.rect(
                game.screen,
                (20, 25, 38),
                notice_rect.inflate(30, 18),
                border_radius=8,
            )

            game.screen.blit(
                notice,
                notice_rect,
            )

        elif current_time >= game.notice_until:
            game.notice_message = ""

    @staticmethod
    def _draw_active_panel(game):
        if game.game_state == "story":
            game.story_panel.draw(
                game.screen,
                game.scenario_engine,
            )

        elif game.game_state == "scenario":
            game.scenario_panel.draw(
                game.screen,
                game.current_scenario,
            )

        elif game.game_state == "feedback":
            game.feedback_panel.draw(
                game.screen,
                game.feedback_message,
                game.feedback_correct,
            )

        elif game.game_state == "complete":
            game.completion_panel.draw(
                game.screen,
                game._build_final_report(),
            )

        elif game.game_state == "day_intro":
            game.day_intro_panel.draw(
                game.screen
            )