from game.adventure.interactable import (
    Interactable,
)

from game.adventure.location import (
    AdventureLocation,
)


SCENARIO_OBJECT_NAMES = {
    # Home phone
    1: "Phone Message",
    7: "Delivery Message",
    10: "QR Giveaway",

    # Home computer
    2: "Game Message",
    8: "Security Email",
    11: "Game Download",

    # School computer
    3: "System Update",
    9: "Browser Warning",
    12: "School Account",

    # School object
    4: "Unknown USB",
    13: "Unknown Charger",
    14: "Lost Tablet",

    # Park
    5: "Online Message",
    15: "Viral Challenge",
    16: "Meeting Request",

    # Internet café
    6: "Wi-Fi Menu",
    17: "Public Computer",
    18: "Open Session",
}


class AdventureWorld:
    def __init__(
        self,
        width,
        height,
        scenario_assignments,
    ):
        room_bounds = (
            30,
            110,
            width - 60,
            height - 150,
        )

        self.scenario_assignments = (
            scenario_assignments
        )

        self.locations = {
            "home": AdventureLocation(
                name="Home",
                bounds=room_bounds,
                player_spawn=(100, 520),
                background_color=(60, 68, 88),
            ),

            "school": AdventureLocation(
                name="School Computer Lab",
                bounds=room_bounds,
                player_spawn=(100, 520),
                background_color=(65, 76, 90),
            ),

            "park": AdventureLocation(
                name="Park",
                bounds=room_bounds,
                player_spawn=(100, 520),
                background_color=(58, 86, 72),
            ),

            "internet_cafe": AdventureLocation(
                name="Internet Café",
                bounds=room_bounds,
                player_spawn=(100, 520),
                background_color=(72, 62, 82),
            ),
        }

        self._build_home()
        self._build_school()
        self._build_park()
        self._build_internet_cafe()

        self.current_location_name = "home"

    @property
    def current_location(self):
        return self.locations[
            self.current_location_name
        ]

    def change_location(
        self,
        location_name,
        player,
    ):
        if location_name not in self.locations:
            return False

        self.current_location_name = location_name

        player.rect.topleft = (
            self.current_location.player_spawn
        )

        return True

    def _scenario_for(
        self,
        slot_name,
    ):
        scenario_id = (
            self.scenario_assignments.get(
                slot_name
            )
        )

        if scenario_id is None:
            raise ValueError(
                f"No scenario assigned to "
                f"slot '{slot_name}'."
            )

        return scenario_id

    def _object_name(
        self,
        scenario_id,
        fallback_name,
    ):
        return SCENARIO_OBJECT_NAMES.get(
            scenario_id,
            fallback_name,
        )

    def get_scenario_objects(
        self,
        location_name=None,
    ):
        if location_name is not None:
            locations = [
                self.locations[location_name]
            ]
        else:
            locations = (
                self.locations.values()
            )

        return [
            interactable
            for location in locations
            for interactable in location.interactables
            if (
                interactable.interaction_type
                == "scenario"
            )
        ]

    def location_completed(
        self,
        location_name,
    ):
        scenario_objects = (
            self.get_scenario_objects(
                location_name
            )
        )

        return bool(
            scenario_objects
        ) and all(
            interactable.completed
            for interactable
            in scenario_objects
        )

    def all_scenarios_completed(self):
        scenario_objects = (
            self.get_scenario_objects()
        )

        return bool(
            scenario_objects
        ) and all(
            interactable.completed
            for interactable
            in scenario_objects
        )

    def can_use_interactable(
        self,
        interactable,
    ):
        if (
            interactable.required_location_complete
            is not None
        ):
            if not self.location_completed(
                interactable
                .required_location_complete
            ):
                return False

        if (
            interactable.requires_all_scenarios
            and not self.all_scenarios_completed()
        ):
            return False

        return True

    def get_lock_message(
        self,
        interactable,
    ):
        required_location = (
            interactable
            .required_location_complete
        )

        if required_location == "home":
            return (
                "Complete both activities at Home "
                "before leaving for School."
            )

        if required_location == "school":
            return (
                "Complete both School activities "
                "before going to the Park."
            )

        if required_location == "park":
            return (
                "Complete the Park event before "
                "going to the Internet Café."
            )

        if required_location == "internet_cafe":
            return (
                "Complete the Café event before "
                "returning Home."
            )

        if interactable.requires_all_scenarios:
            return (
                "Complete all six events before "
                "ending the day."
            )

        return "This interaction is currently locked."

    def _build_home(self):
        home = self.locations["home"]

        phone_scenario = self._scenario_for(
            "home_phone"
        )

        computer_scenario = self._scenario_for(
            "home_computer"
        )

        home.add_interactable(
            Interactable(
                220,
                180,
                110,
                75,
                name=self._object_name(
                    phone_scenario,
                    "Phone",
                ),
                scenario_id=phone_scenario,
                color=(70, 150, 220),
            )
        )

        home.add_interactable(
            Interactable(
                650,
                170,
                130,
                85,
                name=self._object_name(
                    computer_scenario,
                    "Computer",
                ),
                scenario_id=computer_scenario,
                color=(120, 95, 200),
            )
        )

        home.add_interactable(
            Interactable(
                835,
                470,
                80,
                100,
                name="Go to School",
                interaction_type="location",
                target_location="school",
                required_location_complete="home",
                color=(70, 170, 110),
            )
        )

        home.add_interactable(
            Interactable(
                430,
                450,
                130,
                100,
                name="End the Day",
                interaction_type="ending",
                requires_all_scenarios=True,
                color=(170, 125, 75),
            )
        )

    def _build_school(self):
        school = self.locations["school"]

        pc_scenario = self._scenario_for(
            "school_pc"
        )

        object_scenario = self._scenario_for(
            "school_object"
        )

        school.add_interactable(
            Interactable(
                220,
                180,
                120,
                75,
                name=self._object_name(
                    pc_scenario,
                    "School PC",
                ),
                scenario_id=pc_scenario,
                color=(80, 135, 195),
            )
        )

        school.add_interactable(
            Interactable(
                560,
                180,
                120,
                75,
                name=self._object_name(
                    object_scenario,
                    "School Object",
                ),
                scenario_id=object_scenario,
                color=(190, 125, 60),
            )
        )

        school.add_interactable(
            Interactable(
                60,
                470,
                80,
                100,
                name="Return Home",
                interaction_type="location",
                target_location="home",
                color=(70, 170, 110),
            )
        )

        school.add_interactable(
            Interactable(
                835,
                470,
                80,
                100,
                name="Go to Park",
                interaction_type="location",
                target_location="park",
                required_location_complete="school",
                color=(85, 175, 105),
            )
        )

    def _build_park(self):
        park = self.locations["park"]

        park_scenario = self._scenario_for(
            "park_event"
        )

        park.add_interactable(
            Interactable(
                430,
                180,
                130,
                100,
                name=self._object_name(
                    park_scenario,
                    "Park Event",
                ),
                scenario_id=park_scenario,
                color=(75, 145, 210),
            )
        )

        park.add_interactable(
            Interactable(
                60,
                470,
                80,
                100,
                name="Return to School",
                interaction_type="location",
                target_location="school",
                color=(85, 175, 105),
            )
        )

        park.add_interactable(
            Interactable(
                835,
                470,
                80,
                100,
                name="Go to Café",
                interaction_type="location",
                target_location="internet_cafe",
                required_location_complete="park",
                color=(155, 105, 175),
            )
        )

    def _build_internet_cafe(self):
        cafe = self.locations[
            "internet_cafe"
        ]

        cafe_scenario = self._scenario_for(
            "cafe_event"
        )

        cafe.add_interactable(
            Interactable(
                430,
                180,
                130,
                85,
                name=self._object_name(
                    cafe_scenario,
                    "Café Event",
                ),
                scenario_id=cafe_scenario,
                color=(80, 145, 200),
            )
        )

        cafe.add_interactable(
            Interactable(
                60,
                470,
                80,
                100,
                name="Return to Park",
                interaction_type="location",
                target_location="park",
                color=(85, 175, 105),
            )
        )

        cafe.add_interactable(
            Interactable(
                835,
                470,
                80,
                100,
                name="Return Home",
                interaction_type="location",
                target_location="home",
                required_location_complete=(
                    "internet_cafe"
                ),
                color=(70, 170, 110),
            )
        )