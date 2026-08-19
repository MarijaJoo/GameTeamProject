import random


class ScenarioDirector:

    SCENARIO_POOLS = {
        "home_phone": [1, 7, 10],
        "home_computer": [2, 8, 11],
        "school_pc": [3, 9, 12],
        "school_object": [4, 13, 14],
        "park_event": [5, 15, 16],
        "cafe_event": [6, 17, 18],
    }

    def __init__(self, available_scenario_ids, seed=None):
        self.available_scenario_ids = set(
            available_scenario_ids
        )

        # A separate Random object keeps scenario selection
        # isolated from any other random systems in the game.
        self.random = random.Random(seed)

        self.selected_scenarios = (
            self._select_scenarios()
        )

    def _select_scenarios(self):
        selected = {}
        already_selected = set()

        for slot_name, scenario_pool in (
            self.SCENARIO_POOLS.items()
        ):
            valid_scenarios = [
                scenario_id
                for scenario_id in scenario_pool
                if (
                    scenario_id
                    in self.available_scenario_ids
                    and scenario_id
                    not in already_selected
                )
            ]

            if not valid_scenarios:
                raise ValueError(
                    f"No available scenario for slot "
                    f"'{slot_name}'. Pool: {scenario_pool}"
                )

            chosen_id = self.random.choice(
                valid_scenarios
            )

            selected[slot_name] = chosen_id
            already_selected.add(chosen_id)

        return selected

    def get_scenario_id(self, slot_name):
        return self.selected_scenarios.get(
            slot_name
        )

    def print_selection(self):
        print("\nSelected scenarios for this playthrough:")

        for slot_name, scenario_id in (
            self.selected_scenarios.items()
        ):
            print(
                f"  {slot_name}: scenario {scenario_id}"
            )
