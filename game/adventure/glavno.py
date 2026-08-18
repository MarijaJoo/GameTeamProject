import sys

import pygame
from game.ui_folder.story_panel import StoryPanel
from game.adventure.scenario_director import (
    ScenarioDirector,
)
from game.adventure.player import (
    AdventurePlayer,
)
from game.ui_folder.menu_panel import (
    HowToPlayPanel,
    MenuPanel,
)
from game.adventure.settings import (
    BACKGROUND_COLOR,
    FPS,
    GAME_TITLE,
    HEIGHT,
    WIDTH,
)
from game.adventure.game_controller import (
    GameController,
)
from game.adventure.world import (
    AdventureWorld,
)

from game.api_client import (
    GameAPIClient,
)
from game.ui_folder.username_panel import (
    UsernamePanel,
)
from game.ui_folder.fonts import (
    create_game_fonts,
)

from game.ui_folder.game_renderer import (
    GameRenderer,
)
from game.ui_folder.completion_panel import (
    CompletionPanel,
)
from game.ui_folder.feedback_panel import (
    FeedbackPanel,
)
from game.ui_folder.hud import (
    AdventureHUD,
)
from game.ui_folder.scenario_panel import (
    ScenarioPanel,
)
from game.arcade.arcade_game import (
    ArcadeGame,
)

class AdventureGame:
    def __init__(self):

        self.username = None
        self.player_data = None
        self.player_id = None
        self.score = 0
        self.starting_score = 0

        self.api = GameAPIClient(
            mode="auto"
        )

        self.api.connect()

        self.scenarios = self.api.get_scenarios()

        if not self.scenarios:
            raise RuntimeError(
                "No online or offline scenarios were available."
            )

        self.scenarios_by_id = {
            scenario["id"]: scenario
            for scenario in self.scenarios
        }

        available_scenario_ids = list(
            self.scenarios_by_id.keys()
        )

        self.scenario_director = ScenarioDirector(
            available_scenario_ids
        )

        self.scenario_director.print_selection()

        self.starting_score = self.score

        self.total_clues_correct = 0
        self.total_clues_answered = 0

        self.correct_final_decisions = 0
        self.final_decisions_answered = 0

        self.completed_scenario_ids = []
        self.knowledge_modules = {}
        self.knowledge_popup_message = ""
        self.knowledge_popup_until = 0

        self.notice_message = ""
        self.notice_until = 0

        pygame.init()

        self.screen = (
            pygame.display.set_mode(
                (WIDTH, HEIGHT)
            )
        )

        pygame.display.set_caption(
            GAME_TITLE
        )

        self.clock = pygame.time.Clock()

        fonts = create_game_fonts()

        self.title_font = fonts.title
        self.body_font = fonts.body
        self.hud_font = fonts.hud

        self.username_panel = UsernamePanel(
            self.title_font,
            self.body_font,
        )

        self.world = AdventureWorld(
            WIDTH,
            HEIGHT,
            self.scenario_director.selected_scenarios,
        )
        self.arcade_game = ArcadeGame(
            WIDTH,
            HEIGHT,
            self.title_font,
            self.body_font,
        )

        spawn_x, spawn_y = (
            self.world
            .current_location
            .player_spawn
        )

        self.player = AdventurePlayer(
            spawn_x,
            spawn_y,
        )

        self.hud = AdventureHUD(
            self.hud_font,
            self.body_font,
        )

        self.scenario_panel = (
            ScenarioPanel(
                self.title_font,
                self.body_font,
            )
        )

        self.feedback_panel = (
            FeedbackPanel(
                self.title_font,
                self.body_font,
            )
        )

        self.completion_panel = (
            CompletionPanel(
                self.title_font,
                self.body_font,
            )
        )
        self.story_panel = StoryPanel(
            self.title_font,
            self.body_font,
        )
        self.menu_panel = MenuPanel(
            self.title_font,
            self.body_font,
        )

        self.how_to_play_panel = HowToPlayPanel(
            self.title_font,
            self.body_font,
        )

        self.renderer = GameRenderer()

        self.scenario_engine = None

        self.game_state = "username"

        self.current_object = None
        self.current_scenario = None
        self.nearby_object = None

        self.feedback_message = ""
        self.feedback_correct = False

        self.controller = GameController(
            self
        )

        self.running = True



    @property
    def total_score(self):
        return self.score

    def run(self):
        while self.running:
            self.clock.tick(FPS)

            self._find_nearby_object()
            self.controller.handle_events()
            self._update()
            self._draw()

        pygame.quit()
        sys.exit()

    def _find_nearby_object(self):
        self.nearby_object = None

        if self.game_state != "exploring":
            return

        candidate = (
            self.world
            .current_location
            .get_nearby_interactable(
                self.player.rect
            )
        )

        if candidate is None:
            return

        if candidate.interaction_type in (
                "location",
                "ending",
                "arcade_console",
        ):
            self.nearby_object = candidate
            return

        scenario_id = candidate.scenario_id

        if (
                scenario_id is not None
                and scenario_id
                in self.scenarios_by_id
        ):
            self.nearby_object = candidate

    def collect_knowledge_module(
            self,
            collectible,
    ):
        if not collectible.collect():
            return

        self.knowledge_modules[
            collectible.name
        ] = {
            "name": collectible.name,
            "description": (
                collectible.description
            ),
        }

        self.knowledge_popup_message = (
            f"Knowledge collected: "
            f"{collectible.name}"
        )

        self.knowledge_popup_until = (
                pygame.time.get_ticks()
                + 3000
        )

        print(
            f"Collected knowledge module: "
            f"{collectible.name}"
        )

        print(
            collectible.description
        )

        collected = self.get_knowledge_count()

        if collected == 1:
            self.show_notice(
                "Game console unlocked! "
                "Security Defender Level 1 is now available.",
                duration=4500,
            )

        elif collected <= 4:
            self.show_notice(
                (
                    f"Security Defender Level "
                    f"{collected} unlocked!"
                ),
                duration=4000,
            )

    def get_knowledge_count(self):
        return len(
            self.knowledge_modules
        )

    def has_unlocked_arcade(self):
        return (
                self.get_knowledge_count()
                >= 1
        )

    def get_unlocked_arcade_levels(self):
        # One adventure collectible unlocks
        # one arcade level.
        return min(
            self.get_knowledge_count(),
            4,
        )

    def get_knowledge_progress(self):
        return (
            self.get_knowledge_count(),
            4,
        )

    def _handle_menu_event(
            self,
            event,
    ):
        if event.key in (
                pygame.K_w,
                pygame.K_UP,
        ):
            self.menu_panel.move_up()
            return

        if event.key in (
                pygame.K_s,
                pygame.K_DOWN,
        ):
            self.menu_panel.move_down()
            return

        if event.key not in (
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
                pygame.K_SPACE,
        ):
            return

        selected_option = (
            self.menu_panel
            .get_selected_option()
        )

        if selected_option == "Start New Day":
            self._start_new_day()

        elif selected_option == "How to Play":
            self.game_state = "how_to_play"

        elif selected_option == "Quit":
            self.running = False

    def _handle_how_to_play_event(
            self,
            event,
    ):
        if event.key in (
                pygame.K_ESCAPE,
                pygame.K_BACKSPACE,
                pygame.K_RETURN,
        ):
            self.game_state = "menu"

    def show_notice(
            self,
            message,
            duration=2500,
    ):
        self.notice_message = message

        self.notice_until = (
                pygame.time.get_ticks()
                + duration
        )



    def submit_action(
        self,
        selected_action,
    ):
        result = self.api.submit_answer(
            self.player_id,
            self.current_scenario["id"],
            selected_action["id"],
        )

        if (
            result
            and result.get(
                "already_completed"
            )
        ):
            self.feedback_message = (
                result["message"]
            )

            self.feedback_correct = False

            self.current_object.completed = True

        elif result:
            self.score = result[
                "new_score"
            ]

            self.feedback_message = (
                result["animal_message"]
            )

            self.feedback_correct = (
                result["is_correct"]
            )

            self.current_object.completed = True

        else:
            self._process_local_answer(
                selected_action
            )

        self.game_state = "feedback"

    def _process_local_answer(
        self,
        selected_action,
    ):
        self.feedback_correct = (
            selected_action[
                "is_correct"
            ]
        )

        self.feedback_message = (
            selected_action[
                "animal_message"
            ]
        )

        self.score += selected_action[
            "points_modifier"
        ]

        self.score = max(
            0,
            self.score,
        )

        self.current_object.completed = True

    def _all_scenarios_completed(self):
        scenario_objects = (
            self._get_scenario_objects()
        )

        if not scenario_objects:
            return False

        return all(
            interactable.completed
            for interactable
            in scenario_objects
        )

    def _get_scenario_objects(self):
        return [
            interactable
            for location
            in self.world.locations.values()
            for interactable
            in location.interactables
            if (
                    interactable.interaction_type
                    == "scenario"
                    and interactable.scenario_id
                    is not None
                    and interactable.scenario_id
                    in self.scenarios_by_id
            )
        ]

    def submit_arcade_result(
            self,
            level_number,
            arcade_score,
    ):
        result = self.api.submit_arcade_score(
            self.player_id,
            level_number,
            arcade_score,
        )

        if result is None:
            print(
                "Arcade score could not be saved."
            )
            return

        points_added = result.get(
            "points_added",
            0,
        )

        self.score = result.get(
            "new_score",
            self.score,
        )

        print(
            f"Arcade Level {level_number}: "
            f"{arcade_score} points"
        )

        print(
            f"Added to adventure score: "
            f"+{points_added}"
        )

        print(
            f"New total score: "
            f"{self.score}"
        )

    def _update(self):
        if self.game_state == "arcade":
            self.arcade_game.update()

            completed_result = (
                self.arcade_game.take_completed_result()
            )
            if completed_result is not None:
                print(
                    "ARCADE RESULT:",
                    completed_result,
                )
                self.submit_arcade_result(
                    completed_result[
                        "level_number"
                    ],
                    completed_result[
                        "score"
                    ],
                )

            # if not self.arcade_game.active:
            #     return

            return

        if self.game_state != "exploring":
            return

        keys = pygame.key.get_pressed()

        self.player.handle_input(
            keys,
            self.world.current_location.bounds,
            self.world.current_location.collision_rects,
        )
        current_location = (
            self.world.current_location
        )

        current_location.update_collectibles()

        collectible = (
            current_location
            .get_colliding_collectible(
                self.player.rect
            )
        )

        if collectible is not None:
            self.collect_knowledge_module(
                collectible
            )

    def _draw(self):
        self.renderer.draw(self)

    def start_new_day(self):
        available_scenario_ids = list(
            self.scenarios_by_id.keys()
        )

        self.scenario_director = (
            ScenarioDirector(
                available_scenario_ids
            )
        )

        self.scenario_director.print_selection()

        self.world = AdventureWorld(
            WIDTH,
            HEIGHT,
            self.scenario_director
            .selected_scenarios,
        )

        spawn_x, spawn_y = (
            self.world
            .current_location
            .player_spawn
        )

        self.player.rect.topleft = (
            spawn_x,
            spawn_y,
        )

        # Score at the beginning of this particular day.
        self.starting_score = self.score

        # Reset day statistics.
        self.total_clues_correct = 0
        self.total_clues_answered = 0

        self.correct_final_decisions = 0
        self.final_decisions_answered = 0

        self.completed_scenario_ids = []

        # Reset active interaction information.
        self.current_object = None
        self.current_scenario = None
        self.scenario_engine = None
        self.nearby_object = None

        self.feedback_message = ""
        self.feedback_correct = False

        self.notice_message = ""
        self.notice_until = 0
        self.knowledge_modules = {}
        self.knowledge_popup_message = ""
        self.knowledge_popup_until = 0

        self.game_state = "exploring"


    def _build_final_report(self):
        scenario_count = len(
            self._get_scenario_objects()
        )

        return {
            "day_score": (
                    self.score
                    - self.starting_score
            ),
            "total_score": self.score,
            "correct_clues": (
                self.total_clues_correct
            ),
            "total_clues": (
                self.total_clues_answered
            ),
            "correct_decisions": (
                self.correct_final_decisions
            ),
            "total_decisions": (
                self.final_decisions_answered
            ),
            "maximum_score": (
                    scenario_count * 30
            ),
        }