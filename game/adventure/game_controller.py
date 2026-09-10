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

    def __init__(self, game):
        self.game = game
        self.sound_manager = SoundManager()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
                continue

            # Process both Keyboard and Mouse inputs
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self._route_event(event)

    def _route_event(self, event):
        state = self.game.game_state
        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
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
            "language": self._handle_language_event,
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

    def _handle_language_event(self, event):
        game = self.game

        selected_language = (
            game.language_panel.handle_event(event)
        )

        if selected_language is not None:
            game.game_state = "username"


    def _handle_username_event(self, event):
        game = self.game

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game.running = False
                return

            username = game.username_panel.handle_key(event)
            if username is not None:
                self._submit_username(username)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Mouse click to submit username if text is entered
            username = game.username_panel.text.strip()
            if username:
                self._submit_username(username)

    def _submit_username(self, username):
        game = self.game
        game.username = username
        game.player_data = game.api.login_player(game.username)

        if not game.player_data:
            game.username_panel.error_message = (
                "Could not load the player profile."
            )
            return

        game.player_id = game.player_data["id"]
        game.score = game.player_data.get("score", 0)
        game.starting_score = game.score
        game.game_state = "menu"

    def _handle_menu_event(self, event):
        game = self.game

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP):
                game.menu_panel.move_up()
                return

            if event.key in (pygame.K_s, pygame.K_DOWN):
                game.menu_panel.move_down()
                return

            if event.key == pygame.K_ESCAPE:
                game.running = False
                return

            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                selected_option = game.menu_panel.get_selected_option()
                self._execute_menu_option(selected_option)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if hasattr(game.menu_panel, "get_clicked_option"):
                clicked_option = game.menu_panel.get_clicked_option(mouse_pos)
                if clicked_option:
                    self._execute_menu_option(clicked_option)
            else:
                # Fallback: Treat any click as selecting the currently highlighted menu option
                selected_option = game.menu_panel.get_selected_option()
                self._execute_menu_option(selected_option)

    def _execute_menu_option(self, option_text):
        game = self.game
        if option_text == "Почни нов ден":
            game.start_new_day()
            self._update_bgm_for_location("home")
        elif option_text == "Како се игра":
            game.game_state = "how_to_play"
        elif option_text == "Излези":
            game.running = False

    def _handle_how_to_play_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (
                pygame.K_ESCAPE,
                pygame.K_BACKSPACE,
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
                pygame.K_SPACE,
            ):
                self.game.game_state = "menu"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.game.game_state = "menu"


    def _handle_exploring_event(self, event):
        game = self.game

        is_interact_key = (
            event.type == pygame.KEYDOWN
            and event.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER)
        )

        if not is_interact_key or game.nearby_object is None:
            return

        interactable = game.nearby_object

        if not game.world.can_use_interactable(interactable):
            game.show_notice(game.world.get_lock_message(interactable))
            return

        if interactable.interaction_type == "location":
            target_loc = interactable.target_location
            game.world.change_location(interactable.target_location, game.player)
            self._update_bgm_for_location(target_loc)
            game.nearby_object = None
            return

        if interactable.interaction_type == "ending":
            game.game_state = "complete"
            return

        if interactable.interaction_type == "arcade_console":
            if not game.has_unlocked_arcade():
                game.show_notice(
                    "The console is locked. Find a Knowledge Module first.",
                    duration=3000,
                )
                return

            unlocked_levels = game.get_unlocked_arcade_levels()
            game.arcade_game.open_level_select(unlocked_levels)
            game.game_state = "arcade"
            return

        self._start_scenario(interactable)

    def _handle_arcade_event(self, event):
        game = self.game
        should_close = game.arcade_game.handle_event(event)

        if should_close:
            completed_result = (
                game.arcade_game.take_completed_result()
            )

            if completed_result is not None:
                game.submit_arcade_result(
                    completed_result["level_number"],
                    completed_result["score"],
                )

            game.game_state = "exploring"
            game.world.change_location("home", game.player)
            self._update_bgm_for_location("home")
            game.nearby_object = None

    def _start_scenario(self, interactable):
        game = self.game
        game.current_object = interactable
        scenario_id = interactable.scenario_id
        game.current_scenario = game.scenarios_by_id.get(scenario_id)

        if game.current_scenario is None:
            print(f"Scenario ID {scenario_id} was not loaded.")
            game.current_object = None
            return

        script = SCENARIO_SCRIPTS.get(scenario_id)

        if script is None:
            game.game_state = "scenario"
            return

        game.scenario_engine = ScenarioEngine(script, game.current_scenario)
        game.game_state = "story"

    # =========================================================
    # SIMPLE NON-SCRIPTED SCENARIO (1, 2, or Mouse Click)
    # =========================================================

    def _handle_scenario_event(self, event):
        game = self.game

        selected_index = self._get_answer_index(event)

        if selected_index is None:
            return

        if game.current_scenario is None:
            return

        actions = game.current_scenario.get("actions", [])

        if selected_index >= len(actions):
            return

        selected_action = actions[selected_index]

        # Sound SFX trigger
        if selected_action.get("is_correct", False):
            self.sound_manager.play_sfx("correct")
        else:
            self.sound_manager.play_sfx("wrong")

        game.submit_action(selected_action)

    # =========================================================
    # SCRIPTED STORY SCENARIO (1, 2, Space, or Mouse Click)
    # =========================================================

    def _handle_story_event(self, event):
        game = self.game
        engine = game.scenario_engine

        if engine is None:
            return

        # Clue Feedback screen
        if engine.showing_clue_feedback:
            if (
                (event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN))
                or event.type == pygame.MOUSEBUTTONDOWN
            ):
                engine.close_clue_feedback()
            return

        step = engine.current_step
        if step is None:
            return

        step_type = step.get("type")

        # Dialogue state
        if step_type == "dialogue":
            if (
                (event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN))
                or event.type == pygame.MOUSEBUTTONDOWN
            ):
                engine.advance_dialogue()
            return

        # Clue question state
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

        # Final Decision state
        if step_type == "final":
            self._handle_final_decision(event)

    def _handle_final_decision(self, event):
        game = self.game
        engine = game.scenario_engine

        if engine is None:
            return

        selected_index = self._get_answer_index(event)

        if selected_index is None:
            return

        final_answers = engine.script.get("final_answers", [])

        if selected_index >= len(final_answers):
            return

        action_id = self._get_scored_action_id(engine, selected_index)

        if action_id is None:
            return

        selected_action = self._find_action_by_id(engine, action_id)

        if selected_action is None:
            print(
                f"Action ID {action_id} was not found in scenario "
                f"{game.current_scenario['id']}."
            )
            return

        self._record_story_result(engine, selected_action)

        if selected_action.get("is_correct", False):
            self.sound_manager.play_sfx("correct")
        else:
            self.sound_manager.play_sfx("wrong")

        game.submit_action(selected_action)
        engine.complete()

    @staticmethod
    def _get_scored_action_id(engine, selected_index):
        score_action_ids = engine.script.get("score_action_ids", {})
        clue_mapping = score_action_ids.get(engine.clues_correct, {})
        action_id = clue_mapping.get(selected_index)

        if action_id is None:
            print("Missing scoring action for:", engine.clues_correct, selected_index)

        return action_id

    @staticmethod
    def _find_action_by_id(engine, action_id):
        actions = engine.api_scenario.get("actions", [])
        return next((action for action in actions if action.get("id") == action_id), None)

    def _record_story_result(self, engine, selected_action):
        game = self.game

        game.total_clues_correct += engine.clues_correct
        game.total_clues_answered += engine.clues_answered
        game.final_decisions_answered += 1

        if selected_action.get("is_correct", False):
            game.correct_final_decisions += 1

        if game.current_scenario is None:
            return

        scenario_id = game.current_scenario["id"]

        if scenario_id not in game.completed_scenario_ids:
            game.completed_scenario_ids.append(scenario_id)

    def _update_bgm_for_location(self, location_name):
        location_data = LOCATION_MUSIC.get(location_name)
        if location_data:
            music_file, volume = location_data
            self.sound_manager.play_music(music_file, volume=volume)

    # =========================================================
    # FEEDBACK (Space, Enter, or Mouse Click)
    # =========================================================

    def _handle_feedback_event(self, event):
        is_advance = (
            (event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER))
            or event.type == pygame.MOUSEBUTTONDOWN
        )

        if not is_advance:
            return

        game = self.game
        game.current_scenario = None
        game.current_object = None
        game.scenario_engine = None

        game.game_state = "exploring"

    # =========================================================
    # COMPLETION SCREEN (Keyboard + Mouse Click)
    # =========================================================

    def _handle_complete_event(self, event):
        game = self.game

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                game.start_new_day()
            elif event.key in (pygame.K_m, pygame.K_ESCAPE):
                game.game_state = "menu"
            elif event.key in (pygame.K_q, pygame.K_SPACE):
                game.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Advance to menu on mouse click
            game.game_state = "menu"

    # =========================================================
    # SHARED HELPERS (Detects keys 1/2 or Mouse upper/lower click)
    # =========================================================

    def _get_answer_index(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_KP1):
                return 0
            if event.key in (pygame.K_2, pygame.K_KP2):
                return 1

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            panel = getattr(self.game, "scenario_panel", None)

            # Check panel collision if rects exist
            if panel and hasattr(panel, "btn1_rect") and panel.btn1_rect.collidepoint(mouse_pos):
                return 0
            if panel and hasattr(panel, "btn2_rect") and panel.btn2_rect.collidepoint(mouse_pos):
                return 1

            # Fallback: Top half of window = Option 1 (0), Bottom half = Option 2 (1)
            screen_height = pygame.display.get_surface().get_height()
            if mouse_pos[1] < screen_height * 0.65:
                return 0
            else:
                return 1

        return None
