import copy
import time
import requests

from game.localization.localization import OFFLINE_TRANSLATIONS
from game.offline_data import OFFLINE_SCENARIOS


class GameAPIClient:
    VALID_MODES = {"auto", "online", "offline"}

    def __init__(
        self,
        base_url="http://127.0.0.1:8000",
        mode="auto",
    ):
        if mode not in self.VALID_MODES:
            raise ValueError(
                f"Invalid mode: {mode}. "
                f"Expected one of {self.VALID_MODES}."
            )

        self.base_url = base_url
        self.mode = mode
        self.online = False

        self.offline_score = 0
        self.offline_completed_scenarios = set()
        self.offline_arcade_best_scores = {}

    def connect(self, timeout_seconds=180, retry_interval=2):
        if self.mode == "offline":
            self.online = False
            return False

        deadline = time.time() + max(0, timeout_seconds)
        last_error = None
        while time.time() < deadline:
            try:
                response = requests.get(
                    f"{self.base_url}/scenarios/",
                    timeout=3,
                )

                response.raise_for_status()
                self.online = True
                return True

            except requests.RequestException as error:
                last_error=error
                time.sleep(retry_interval)
        self.online = False

        if self.mode == "online":
            raise ConnectionError(
                "Online mode was selected, but the API "
                "could not be reached."
            ) from error

        print("API unavailable. Continuing in offline mode.")

        return False

    def login_player(self, username):
        if not self.online:
            return {
                "id": 1,
                "username": username,
                "score": self.offline_score,
                "offline": True,
            }

        try:
            response = requests.post(
                f"{self.base_url}/players/",
                json={
                    "username": username,
                    "score": 0,
                },
                timeout=3,
            )

            response.raise_for_status()
            return response.json()

        except requests.RequestException:
            return self._switch_to_offline_player(username)

    def get_scenarios(self):
        if not self.online:
            return copy.deepcopy(OFFLINE_SCENARIOS)

        try:
            response = requests.get(
                f"{self.base_url}/scenarios/",
                timeout=3,
            )

            response.raise_for_status()
            return response.json()

        except requests.RequestException:
            self.online = False
            print(
                "Connection lost. Loading offline scenarios."
            )

            return copy.deepcopy(OFFLINE_SCENARIOS)

    def submit_answer(
        self,
        player_id,
        scenario_id,
        action_id,
    ):
        if not self.online:
            return self._submit_offline_answer(
                scenario_id,
                action_id,
            )

        try:
            response = requests.post(
                f"{self.base_url}/progress/",
                json={
                    "player_id": player_id,
                    "scenario_id": scenario_id,
                    "action_id": action_id,
                },
                timeout=3,
            )

            if response.status_code == 400:
                return {
                    "already_completed": True,
                    "message": response.json().get(
                        "detail",
                        "This scenario was already completed.",
                    ),
                }

            response.raise_for_status()
            return response.json()

        except requests.RequestException:
            self.online = False

            print(
                "Connection lost. Answer will be processed "
                "in offline mode."
            )

            return self._submit_offline_answer(
                scenario_id,
                action_id,
            )

    def submit_arcade_score(
            self,
            player_id,
            level_number,
            score,
    ):
        if not self.online:
            old_best = (
                self.offline_arcade_best_scores.get(
                    level_number,
                    0,
                )
            )

            points_added = max(
                0,
                score - old_best,
            )

            if score > old_best:
                self.offline_arcade_best_scores[
                    level_number
                ] = score

            self.offline_score += points_added

            return {
                "status": "offline_success",
                "level_number": level_number,
                "submitted_score": score,
                "best_score": max(
                    old_best,
                    score,
                ),
                "points_added": points_added,
                "new_score": self.offline_score,
                "offline": True,
            }

        try:
            response = requests.post(
                (
                    f"{self.base_url}/players/"
                    f"{player_id}/arcade-score/"
                ),
                json={
                    "level_number": level_number,
                    "score": score,
                },
                timeout=3,
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as error:
            print(
                "Could not submit arcade score:",
                error,
            )

            return None

    def _submit_offline_answer(
        self,
        scenario_id,
        action_id,
    ):
        if scenario_id in self.offline_completed_scenarios:
            return {
                "already_completed": True,
                "message": (
                    "This scenario was already completed "
                    "during the current offline session."
                ),
            }

        scenario = next(
            (
                item
                for item in OFFLINE_SCENARIOS
                if item["id"] == scenario_id
            ),
            None,
        )

        if scenario is None:
            return None

        action = next(
            (
                item
                for item in scenario["actions"]
                if item["id"] == action_id
            ),
            None,
        )

        if action is None:
            return None

        self.offline_completed_scenarios.add(scenario_id)

        self.offline_score += action["points_modifier"]
        self.offline_score = max(0, self.offline_score)

        return {
            "status": "offline_success",
            "new_score": self.offline_score,
            "animal_message": action["animal_message"],
            "is_correct": action["is_correct"],
            "offline": True,
        }

    def _switch_to_offline_player(self, username):
        self.online = False

        return {
            "id": 1,
            "username": username,
            "score": self.offline_score,
            "offline": True,
        }

    def get_translations(self, language):
        if not self.online:
            return copy.deepcopy(OFFLINE_TRANSLATIONS.get(language, {}))

        try:
            response = requests.get(
                f"{self.base_url}/translations/{language}",
                timeout=3,
            )

            response.raise_for_status()
            return response.json()

        except requests.RequestException:
            self.online = False
            print(
                f"Connection lost. Loading offline translations for {language}."
            )
            return copy.deepcopy(OFFLINE_TRANSLATIONS.get(language, {}))

