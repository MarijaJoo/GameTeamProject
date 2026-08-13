import pygame

from game.adventure.asset_loader import SoundManager
from game.adventure.scenario_engine import ScenarioEngine
from game.adventure.scenarios import SCENARIO_SCRIPTS

LOCATION_MUSIC = {
    "home": ("home.mp3", 0.20),
    "school": ("school.mp3", 0.10),
    "cafe": ("cafe.mp3", 0.10),
    "internet_cafe": ("cafe.mp3", 0.10),
    "internet cafe": ("cafe.mp3", 0.10),
    "park": ("park.mp3", 0.20),
}


class GameController:
    """
    Handles keyboard events and game-state transitions.

    The AdventureGame object still owns the world, player,
    API connection, score, panels, and active scenario data.
    """

    def __init__(self, game):
        self.game = game
        self.sound_manager = SoundManager()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
                continue

            if event.type != pygame.KEYDOWN:
                continue

            self._route_key_event(event)

    def _route_key_event(self, event):
        state = self.game.game_state

        # Username and menu screens handle Escape themselves.
        if (
            event.key == pygame.K_ESCAPE
            and state not in (
                "username",
                "menu",
                "how_to_play",
                "complete",
                "arcade",
            )
        ):
            self.game.running = False
            return

        handlers = {
            "username": self._handle_username_event,
            "menu": self._handle_menu_event,
            "how_to_play": self._handle_how_to_play_event,
            "exploring": self._handle_exploring_event,
            "story": self._handle_story_event,
            "scenario": self._handle_scenario_event,
            "feedback": self._handle_feedback_event,
            "complete": self._handle_complete_event,
            "arcade": self._handle_arcade_event,
        }

        handler = handlers.get(state)

        if handler is not None:
            handler(event)

    # =========================================================
    # USERNAME
    # =========================================================

    def _handle_username_event(self, event):
        game = self.game

        if event.key == pygame.K_ESCAPE:
            game.running = False
            return

        username = game.username_panel.handle_key(
            event
        )

        if username is None:
            return

        game.username = username

        game.player_data = game.api.login_player(
            game.username
        )

        if not game.player_data:
            game.username_panel.error_message = (
                "Could not load the player profile."
            )
            return

        game.player_id = game.player_data["id"]

        game.score = game.player_data.get(
            "score",
            0,
        )

        game.starting_score = game.score
        game.game_state = "menu"

    # =========================================================
    # MAIN MENU
    # =========================================================

    def _handle_menu_event(self, event):
        game = self.game

        if event.key in (
            pygame.K_w,
            pygame.K_UP,
        ):
            game.menu_panel.move_up()
            return

        if event.key in (
            pygame.K_s,
            pygame.K_DOWN,
        ):
            game.menu_panel.move_down()
            return

        if event.key == pygame.K_ESCAPE:
            game.running = False
            return

        if event.key not in (
            pygame.K_RETURN,
            pygame.K_KP_ENTER,
            pygame.K_SPACE,
        ):
            return

        selected_option = (
            game.menu_panel.get_selected_option()
        )

        if selected_option == "Start New Day":
            game.start_new_day()
            self._update_bgm_for_location("home")

        elif selected_option == "How to Play":
            game.game_state = "how_to_play"

        elif selected_option == "Quit":
            game.running = False

    # =========================================================
    # HOW TO PLAY
    # =========================================================

    def _handle_how_to_play_event(
        self,
        event,
    ):
        if event.key in (
            pygame.K_ESCAPE,
            pygame.K_BACKSPACE,
            pygame.K_RETURN,
            pygame.K_KP_ENTER,
        ):
            self.game.game_state = "menu"

    # =========================================================
    # EXPLORING
    # =========================================================

    def _handle_exploring_event(
        self,
        event,
    ):
        game = self.game

        if (
            event.key != pygame.K_e
            or game.nearby_object is None
        ):
            return

        interactable = game.nearby_object

        if not game.world.can_use_interactable(
            interactable
        ):
            game.show_notice(
                game.world.get_lock_message(
                    interactable
                )
            )
            return

        if (
            interactable.interaction_type
            == "location"
        ):
            target_loc = interactable.target_location
            game.world.change_location(
                interactable.target_location,
                game.player,
            )
            self._update_bgm_for_location(target_loc)
            game.nearby_object = None
            return

        if (
            interactable.interaction_type
            == "ending"
        ):
            game.game_state = "complete"
            return

        if (
                interactable.interaction_type
                == "arcade_console"
        ):
            collected, required = (
                game.get_knowledge_progress()
            )

            if not game.has_unlocked_arcade():
                game.show_notice(
                    (
                        "The console is locked. "
                        "Find a Knowledge Module first."
                    ),
                    duration=3000,
                )
                return

            unlocked_levels = (
                game.get_unlocked_arcade_levels()
            )

            game.arcade_game.open_level_select(
                unlocked_levels
            )

            game.game_state = "arcade"
            return

        self._start_scenario(
            interactable
        )

    def _handle_arcade_event(
            self,
            event,
    ):
        game = self.game

        should_close = (
            game.arcade_game.handle_event(
                event
            )
        )

        if should_close:
            game.game_state = "exploring"

            game.world.change_location(
                "home",
                game.player,
            )
            self._update_bgm_for_location("home")
            game.nearby_object = None

    def _start_scenario(
        self,
        interactable,
    ):
        game = self.game

        game.current_object = interactable

        scenario_id = interactable.scenario_id

        game.current_scenario = (
            game.scenarios_by_id.get(
                scenario_id
            )
        )

        if game.current_scenario is None:
            print(
                f"Scenario ID {scenario_id} "
                "was not loaded."
            )

            game.current_object = None
            return

        script = SCENARIO_SCRIPTS.get(
            scenario_id
        )

        if script is None:
            game.game_state = "scenario"
            return

        game.scenario_engine = ScenarioEngine(
            script,
            game.current_scenario,
        )

        game.game_state = "story"

    # =========================================================
    # SIMPLE NON-SCRIPTED SCENARIO
    # =========================================================

    def _handle_scenario_event(
        self,
        event,
    ):
        game = self.game

        selected_index = self._get_answer_index(
            event
        )

        if selected_index is None:
            return

        if game.current_scenario is None:
            return

        actions = game.current_scenario.get(
            "actions",
            [],
        )

        if selected_index >= len(actions):
            return

        selected_action = actions[
            selected_index
        ]

        # sfx trigger
        if selected_action.get("is_correct", False):
            self.sound_manager.play_sfx("correct")
        else:
            self.sound_manager.play_sfx("wrong")

        game.submit_action(
            selected_action
        )

    # =========================================================
    # SCRIPTED STORY SCENARIO
    # =========================================================

    def _handle_story_event(
        self,
        event,
    ):
        game = self.game
        engine = game.scenario_engine

        if engine is None:
            return

        if engine.showing_clue_feedback:
            if event.key == pygame.K_SPACE:
                engine.close_clue_feedback()

            return

        step = engine.current_step

        if step is None:
            return

        step_type = step.get("type")

        if step_type == "dialogue":
            if event.key == pygame.K_SPACE:
                engine.advance_dialogue()

            return

        if step_type == "clue":
            selected_index = self._get_answer_index(event)

            if selected_index is not None:
                before_correct = engine.clues_correct

                engine.answer_clue(selected_index)

                if engine.clues_correct > before_correct:
                    self.sound_manager.play_sfx("correct")
                else:
                    self.sound_manager.play_sfx("wrong")

            return

        if step_type == "final":
            self._handle_final_decision(
                event
            )

    def _handle_final_decision(
        self,
        event,
    ):
        game = self.game
        engine = game.scenario_engine

        if engine is None:
            return

        selected_index = self._get_answer_index(
            event
        )

        if selected_index is None:
            return

        final_answers = engine.script.get(
            "final_answers",
            [],
        )

        if selected_index >= len(
            final_answers
        ):
            return

        action_id = self._get_scored_action_id(
            engine,
            selected_index,
        )

        if action_id is None:
            return

        selected_action = (
            self._find_action_by_id(
                engine,
                action_id,
            )
        )

        if selected_action is None:
            print(
                f"Action ID {action_id} "
                "was not found in scenario "
                f"{game.current_scenario['id']}."
            )
            return

        self._record_story_result(
            engine,
            selected_action,
        )

        # wrong/correct
        if selected_action.get("is_correct", False):
            self.sound_manager.play_sfx("correct")
        else:
            self.sound_manager.play_sfx("wrong")

        game.submit_action(
            selected_action
        )

        engine.complete()

    @staticmethod
    def _get_scored_action_id(
        engine,
        selected_index,
    ):
        score_action_ids = (
            engine.script.get(
                "score_action_ids",
                {},
            )
        )

        clue_mapping = (
            score_action_ids.get(
                engine.clues_correct,
                {},
            )
        )

        action_id = clue_mapping.get(
            selected_index
        )

        if action_id is None:
            print(
                "Missing scoring action for:",
                engine.clues_correct,
                selected_index,
            )

        return action_id

    @staticmethod
    def _find_action_by_id(
        engine,
        action_id,
    ):
        actions = engine.api_scenario.get(
            "actions",
            [],
        )

        return next(
            (
                action
                for action in actions
                if action.get("id")
                == action_id
            ),
            None,
        )

    def _record_story_result(
        self,
        engine,
        selected_action,
    ):
        game = self.game

        game.total_clues_correct += (
            engine.clues_correct
        )

        game.total_clues_answered += (
            engine.clues_answered
        )

        game.final_decisions_answered += 1

        if selected_action.get(
            "is_correct",
            False,
        ):
            game.correct_final_decisions += 1

        if game.current_scenario is None:
            return

        scenario_id = (
            game.current_scenario["id"]
        )

        if (
            scenario_id
            not in game.completed_scenario_ids
        ):
            game.completed_scenario_ids.append(
                scenario_id
            )


    def _update_bgm_for_location(self, location_name):
        location_data = LOCATION_MUSIC.get(location_name)
        if location_data:
            music_file, volume = location_data
            self.sound_manager.play_music(music_file, volume=volume)

    # =========================================================
    # FEEDBACK
    # =========================================================

    def _handle_feedback_event(
        self,
        event,
    ):
        if event.key != pygame.K_SPACE:
            return

        game = self.game

        game.current_scenario = None
        game.current_object = None
        game.scenario_engine = None

        game.game_state = "exploring"

    # =========================================================
    # COMPLETION SCREEN
    # =========================================================

    def _handle_complete_event(
        self,
        event,
    ):
        game = self.game

        if event.key == pygame.K_r:
            game.start_new_day()

        elif event.key in (
            pygame.K_m,
            pygame.K_ESCAPE,
        ):
            game.game_state = "menu"

        elif event.key in (
            pygame.K_q,
            pygame.K_SPACE,
        ):
            game.running = False

    # =========================================================
    # SHARED HELPERS
    # =========================================================

    @staticmethod
    def _get_answer_index(
        event,
    ):
        if event.key in (
            pygame.K_1,
            pygame.K_KP1,
        ):
            return 0

        if event.key in (
            pygame.K_2,
            pygame.K_KP2,
        ):
            return 1

        return None