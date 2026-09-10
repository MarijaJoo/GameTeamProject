from game.adventure.interactable import (
    Interactable,
)

from game.adventure.location import (
    AdventureLocation,
)
from game.adventure.asset_loader import (
    load_image,
)

from game.adventure.settings import (
    DEBUG_UNLOCK_ALL_LOCATIONS,
)

from game.adventure.knowledge_collectible import (
    KnowledgeCollectible,
)
from game.localization import t
# SCENARIO_OBJECT_NAMES = {
#     # Home phone
#     1: "Phone Message",
#     7: "Delivery Message",
#     10: "QR Giveaway",
#
#     # Home computer
#     2: "Game Message",
#     8: "Security Email",
#     11: "Game Download",
#
#     # School computer
#     3: "System Update",
#     9: "Browser Warning",
#     12: "School Account",
#
#     # School object
#     4: "Unknown USB",
#     13: "Unknown Charger",
#     14: "Lost Tablet",
#
#     # Park
#     5: "Online Message",
#     15: "Viral Challenge",
#     16: "Meeting Request",
#
#     # Internet café
#     6: "Wi-Fi Menu",
#     17: "Public Computer",
#     18: "Open Session",
# }

SCENARIO_OBJECT_NAMES = {
    1: "Телефонска порака",
    7: "Порака за достава",
    10: "QR наградна игра",

    2: "Порака за игра",
    8: "Безбедносен е-пошта",
    11: "Преземање игра",

    3: "Системско ажурирање",
    9: "Предупредување од прелистувачот",
    12: "Училишна сметка",

    4: "Непознат USB",
    13: "Непознат полнач",
    14: "Изгубен таблет",

    5: "Онлајн порака",
    15: "Вирален предизвик",
    16: "Барање за средба",

    6: "Wi-Fi мени",
    17: "Јавен компјутер",
    18: "Отворена сесија",
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

        background_size = (
            room_bounds[2],
            room_bounds[3],
        )

        home_background = load_image(
            "backgrounds/home.png",
            size=background_size,
        )

        school_background = load_image(
            "backgrounds/school.png",
            size=background_size,
        )

        park_background = load_image(
            "backgrounds/park.png",
            size=background_size,
        )

        cafe_background = load_image(
            "backgrounds/internet_cafe.png",
            size=background_size,
        )

        self.locations = {
            "home": AdventureLocation(
                name=t("Дома"),
                bounds=room_bounds,
                player_spawn=(470, 540),
                background_color=(60, 68, 88),
                background_image=home_background,
            ),

            "school": AdventureLocation(
                name=t("Училишна компјутерска лабораторија"),
                bounds=room_bounds,
                player_spawn=(100, 520),
                background_color=(65, 76, 90),
                background_image=school_background,
            ),

            "park": AdventureLocation(
                name=t("Парк"),
                bounds=room_bounds,
                player_spawn=(100, 520),
                background_color=(58, 86, 72),
                background_image=park_background,
            ),

            "internet_cafe": AdventureLocation(
                name=t("Интернет кафе"),
                bounds=room_bounds,
                player_spawn=(100, 520),
                background_color=(72, 62, 82),
                background_image=cafe_background,
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
        return t(
            SCENARIO_OBJECT_NAMES.get(
                scenario_id,
                fallback_name,
            )
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
        if DEBUG_UNLOCK_ALL_LOCATIONS:
            return True
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
                t(
                    "Заврши ги двете активности дома "
                    "пред да заминеш во училиште."
                )
            )

        if required_location == "school":
            return (
                 t(
        "Заврши ги двете активности во училиште "
        "пред да одиш во парк."
    )
            )

        if required_location == "park":
            return (
                t(
                    "Заврши ја активноста во паркот "
                    "пред да одиш во интернет кафето."
                )
            )

        if required_location == "internet_cafe":
            return t(
                "Заврши ја активноста во интернет кафето "
                "пред да се вратиш дома."
            )

        if interactable.requires_all_scenarios:
            return (
                t(
                    "Заврши ги сите шест настани "
                    "пред да го завршиш денот."
                )
            )

        return t(
            "Оваа интеракција моментално е заклучена."
        )

    def _build_home(self):
        home = self.locations["home"]

        phone_scenario = self._scenario_for(
            "home_phone"
        )

        computer_scenario = self._scenario_for(
            "home_computer"
        )

        home.add_interactable(
            Interactable(230,525,65,55,
                name=self._object_name(phone_scenario,"Телефон",),
                scenario_id=phone_scenario,
                show_placeholder=False,
            )
        )

        home.add_interactable(
            Interactable(340,205,170,110,
                name=self._object_name(computer_scenario,"Компјутер",),
                scenario_id=computer_scenario,
                show_placeholder=False,
            )
        )

        home.add_interactable(
            Interactable(448,585,110,60,
                name=t("Оди во училиште"),
                interaction_type="location",
                target_location="school",
                required_location_complete="home",
                show_placeholder=False,
            )
        )
        home.add_interactable(
            Interactable(
                760,
                370,
                120,
                100,
                name="",
                interaction_type="arcade_console",
                show_placeholder=False,
            )
        )

        home.add_interactable(
            Interactable(95,210,130,180,
                name=t("Заврши го денот"),
                interaction_type="ending",
                requires_all_scenarios=True,
                show_placeholder=False,
            )
        )
        home.add_collectible(
            KnowledgeCollectible(
                x=860,
                y=270,
                name=t("Менаџер за лозинки"),
                description=t(
                    "Менаџерот за лозинки чува силни, уникатни "
                    "лозинки во шифриран трезор."
                ),
            )
        )

        # Top-left bed and nightstand area
        home.add_collision(55,150,900,150,)
        #bed
        home.add_collision(55, 130, 165, 270, )

        # Computer desk area
        home.add_collision(320,150,265,155,)

        # Left TV cabinet
        home.add_collision(50,390,100,160, )

        # Right sofa / cabinet area
        home.add_collision(780,370,150,140, )
        # bottom plant shelf
        home.add_collision(190, 530, 90, 100, )
        home.add_collision(30, 590, 900, 30, )

    def _build_school(self):
        school = self.locations["school"]

        pc_scenario = self._scenario_for(
            "school_pc"
        )

        object_scenario = self._scenario_for(
            "school_object"
        )

        school.add_interactable(
            Interactable(730,300,70,75,
                name=self._object_name(pc_scenario,"Училишен компјутер"),
                scenario_id=pc_scenario,
                show_placeholder=False,
            )
        )

        school.add_interactable(
            Interactable(60,320,90,155,
                name=self._object_name(object_scenario,"Училишен предме",),
                scenario_id=object_scenario,
                show_placeholder=False,
            )
        )

        school.add_interactable(
            Interactable(460,590,80,100,
                name=t("Врати се дома"),
                interaction_type="location",
                target_location="home",
                show_placeholder=False,
            )
        )

        school.add_interactable(
            Interactable(885,270,80,100,
                name=t("Оди во парк"),
                interaction_type="location",
                target_location="park",
                required_location_complete="school",
                show_placeholder=False,
            )
        )

        school.add_collectible(
            KnowledgeCollectible(
                x=325,
                y=200,
                name=t("Шифриран USB"),
                description=t(
                    "Енкрипцијата ги штити датотеките со тоа што"
                    "ги прави нечитливи без точниот клуч."
                ),
            )
        )

        #computers
        school.add_collision(250, 320, 50, 85, )
        school.add_collision(350, 320, 50, 85, )
        school.add_collision(450, 320, 50, 85, )
        school.add_collision(550, 320, 50, 85, )
        school.add_collision(650, 320, 50, 85, )
        school.add_collision(750, 320, 50, 85, )

        school.add_collision(700, 450, 50, 85, )
        school.add_collision(300, 450, 50, 85, )
        school.add_collision(400, 450, 50, 85, )
        school.add_collision(500, 450, 50, 85, )
        school.add_collision(600, 450, 50, 85, )

        #wall
        school.add_collision(55, 130, 900, 90, )

        school.add_collision(250, 200, 100, 70, )
        school.add_collision(50, 320, 50, 205, )



    def _build_park(self):
        park = self.locations["park"]

        park_scenario = self._scenario_for(
            "park_event"
        )

        park.add_interactable(
            Interactable(
                190,
                220,
                130,
                100,
                name=self._object_name(
                    park_scenario,
                    "Park Event",
                ),
                scenario_id=park_scenario,
                show_placeholder=False,
            )
        )

        park.add_interactable(
            Interactable(
                280,
                580,
                80,
                80,
                name=t("Врати се во училиште"),
                interaction_type="location",
                target_location="school",
                show_placeholder=False,
            )
        )

        park.add_interactable(
            Interactable(
                895,
                150,
                80,
                100,
                name=t("Оди во кафе"),
                interaction_type="location",
                target_location="internet_cafe",
                required_location_complete="park",
                show_placeholder=False,
            )
        )
        park.add_collectible(
            KnowledgeCollectible(
                x=780,
                y=360,
                name=t("Безбедносна картичка"),
                description=t(
                    "Безбедносните картички помагаат во контролата на физичкиот пристап до заштитените згради и системи."
                ),
            )
        )

        #benches
        park.add_collision(120, 150, 150, 40, )
        park.add_collision(520, 130, 190, 40, )
        park.add_collision(90, 250, 30, 70, )
        park.add_collision(90, 430, 30, 70, )

        #water
        park.add_collision(800, 220, 190, 450, )
        park.add_collision(480, 390, 150, 200, )
        park.add_collision(550, 290, 250, 70, )
        park.add_collision(690, 410, 200, 200, )


    def _build_internet_cafe(self):
        cafe = self.locations[
            "internet_cafe"
        ]

        cafe_scenario = self._scenario_for(
            "cafe_event"
        )

        cafe.add_interactable(
            Interactable(730,460,130,85,
                name=self._object_name(cafe_scenario,"Настан во интернет кафе"),
                scenario_id=cafe_scenario,
                show_placeholder=False,
            )
        )

        cafe.add_interactable(
            Interactable(455,580,120,40,
                name=t("Врати се дома"),
                interaction_type="location",
                target_location="home",
                required_location_complete=("internet_cafe"),
                show_placeholder=False,
            )
        )
        cafe.add_collectible(
            KnowledgeCollectible(
                x=70,
                y=195,
                name=t("VPN токен"),
                description=t(
                    "VPN го енкриптира мрежниот сообраќај помеѓу вашиот "
                    "уред и VPN услугата."
                ),
            )
        )

        cafe.add_collision(60, 270, 350, 70, )
        cafe.add_collision(560, 280, 310, 100, )
        cafe.add_collision(580, 460, 390, 60, )
        cafe.add_collision(60, 120, 910, 100, )
        cafe.add_collision(60, 600, 910, 70, )
