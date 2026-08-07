from pathlib import Path

import pygame

from game.arcade.arcade_collectible import (
    ArcadeCollectible,
)
from game.arcade.arcade_settings import (
    ARCADE_WALL_BORDER_COLOR,
    ARCADE_WALL_COLOR,
    TILE_SIZE,
)
import random

from game.arcade.knowledge_dot import (
    KnowledgeDot,
)

from game.arcade.knowledge_topics import (
    KNOWLEDGE_TOPICS,
)
from game.arcade.software_update import (
    SoftwareUpdate,
)


class ArcadeMap:
    def __init__(
        self,
        level_filename,
    ):
        self.level_path = (
            Path(__file__).resolve().parent
            / "levels"
            / level_filename
        )

        self.map_data = []

        self.walls = []
        self.collectibles = []
        self.knowledge_dots = []
        self.software_updates = []
        self.enemy_spawns = []
        self.player_spawn = (
            TILE_SIZE,
            TILE_SIZE,
        )

        self.rows = 0
        self.columns = 0

        self.width = 0
        self.height = 0

        self._load_level()

    def _load_level(self):
        if not self.level_path.exists():
            raise FileNotFoundError(
                f"Arcade level was not found: "
                f"{self.level_path}"
            )

        with open(
            self.level_path,
            "r",
            encoding="utf-8",
        ) as level_file:
            self.map_data = [
                line.rstrip("\n")
                for line in level_file
                if line.rstrip("\n")
            ]

        if not self.map_data:
            raise ValueError(
                "The arcade level is empty."
            )

        expected_width = len(
            self.map_data[0]
        )

        for row_number, line in enumerate(
            self.map_data,
            start=1,
        ):
            if len(line) != expected_width:
                raise ValueError(
                    "Every arcade-map row must "
                    "have the same length. "
                    f"Row {row_number} has "
                    f"{len(line)} characters; "
                    f"expected {expected_width}."
                )

        self.rows = len(
            self.map_data
        )

        self.columns = expected_width

        self.width = (
            self.columns
            * TILE_SIZE
        )

        self.height = (
            self.rows
            * TILE_SIZE
        )

        self._build_level_objects()

    def _build_level_objects(self):
        self.walls = []
        self.collectibles = []
        self.knowledge_dots = []
        self.enemy_spawns = []
        self.software_updates = []

        knowledge_positions = []

        for row, line in enumerate(
                self.map_data
        ):
            for column, tile in enumerate(
                    line
            ):
                tile_x = (
                        column * TILE_SIZE
                )

                tile_y = (
                        row * TILE_SIZE
                )

                tile_center_x = (
                        tile_x + TILE_SIZE // 2
                )

                tile_center_y = (
                        tile_y + TILE_SIZE // 2
                )

                if tile == "#":
                    self.walls.append(
                        pygame.Rect(
                            tile_x,
                            tile_y,
                            TILE_SIZE,
                            TILE_SIZE,
                        )
                    )

                elif tile == ".":
                    self.collectibles.append(
                        ArcadeCollectible(
                            tile_center_x,
                            tile_center_y,
                        )
                    )

                elif tile == "K":
                    knowledge_positions.append(
                        (
                            tile_center_x,
                            tile_center_y,
                        )
                    )

                elif tile == "P":
                    self.player_spawn = (
                        tile_center_x,
                        tile_center_y,
                    )

                elif tile == "V":
                    self.enemy_spawns.append(
                        (
                            tile_center_x,
                            tile_center_y,
                        )
                    )
                elif tile == "U":
                    self.software_updates.append(
                        SoftwareUpdate(
                            tile_center_x,
                            tile_center_y,
                        )
                    )

        selected_topics = random.sample(
            KNOWLEDGE_TOPICS,
            k=min(
                len(knowledge_positions),
                len(KNOWLEDGE_TOPICS),
            ),
        )

        for position, topic in zip(
                knowledge_positions,
                selected_topics,
        ):
            self.knowledge_dots.append(
                KnowledgeDot(
                    position[0],
                    position[1],
                    topic,
                )
            )

    def reset_collectibles(self):
        for collectible in (
            self.collectibles
        ):
            collectible.collected = False

    def reset_knowledge_dots(self):
        for knowledge_dot in self.knowledge_dots:
            knowledge_dot.collected = False

    def get_remaining_collectibles(
        self,
    ):
        return sum(
            not collectible.collected
            for collectible
            in self.collectibles
        )

    def all_collectibles_collected(self):
        small_dots_finished = (
                self.get_remaining_collectibles() == 0
        )

        knowledge_finished = all(
            knowledge_dot.collected
            for knowledge_dot in self.knowledge_dots
        )

        return (
                small_dots_finished
                and knowledge_finished
        )

    def check_collectible_collision(
        self,
        player_rect,
    ):
        collected_count = 0

        for collectible in (
            self.collectibles
        ):
            if (
                not collectible.collected
                and player_rect.colliderect(
                    collectible.rect
                )
            ):
                if collectible.collect():
                    collected_count += 1

        return collected_count

    def reset_software_updates(self):
        for software_update in (
                self.software_updates
        ):
            software_update.reset()

    def update_software_updates(self):
        for software_update in (
                self.software_updates
        ):
            software_update.update()

    def check_software_update_collision(
            self,
            player_rect,
    ):
        for software_update in (
                self.software_updates
        ):
            if (
                    not software_update.collected
                    and player_rect.colliderect(
                software_update.rect
            )
            ):
                if software_update.collect():
                    return software_update

        return None

    def update_knowledge_dots(self):
        for knowledge_dot in self.knowledge_dots:
            knowledge_dot.update()

    def check_knowledge_collision(
            self,
            player_rect,
    ):
        for knowledge_dot in self.knowledge_dots:
            if (
                    not knowledge_dot.collected
                    and player_rect.colliderect(
                knowledge_dot.rect
            )
            ):
                if knowledge_dot.collect():
                    return knowledge_dot

        return None

    def draw(
        self,
        screen,
        offset_x,
        offset_y,
    ):
        for wall in self.walls:
            draw_rect = wall.move(
                offset_x,
                offset_y,
            )

            pygame.draw.rect(
                screen,
                ARCADE_WALL_COLOR,
                draw_rect,
                border_radius=5,
            )

            pygame.draw.rect(
                screen,
                ARCADE_WALL_BORDER_COLOR,
                draw_rect,
                2,
                border_radius=5,
            )

        for collectible in (
            self.collectibles
        ):
            collectible.draw(
                screen,
                offset_x,
                offset_y,
            )

        for knowledge_dot in self.knowledge_dots:
            knowledge_dot.draw(
                screen,
                offset_x,
                offset_y,
            )

        for software_update in (
                self.software_updates
        ):
            software_update.draw(
                screen,
                offset_x,
                offset_y,
            )