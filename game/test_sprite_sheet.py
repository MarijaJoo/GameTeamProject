import sys

import pygame

from game.adventure.asset_loader import (
    load_sprite_sheet,
)
from game.adventure.sprite_sheet import (
    slice_sprite_sheet,
)


pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 500

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pygame.display.set_caption(
    "Sprite Sheet Frame Viewer"
)

clock = pygame.time.Clock()

font = pygame.font.SysFont(
    "arial",
    18,
)

sheet = load_sprite_sheet(
    "player/walk_sheet.png"
)

if sheet is None:
    pygame.quit()
    sys.exit()

frames = slice_sprite_sheet(
    sheet,
    frame_width=16,
    frame_height=32,
)

SCALE = 4
FRAME_GAP = 20
FRAMES_PER_ROW = 12

running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
        ):
            running = False

    screen.fill((35, 38, 48))

    for index, frame in enumerate(frames):
        row = index // FRAMES_PER_ROW
        column = index % FRAMES_PER_ROW

        scaled_frame = pygame.transform.scale(
            frame,
            (
                frame.get_width() * SCALE,
                frame.get_height() * SCALE,
            ),
        )

        x = 25 + column * (
            scaled_frame.get_width()
            + FRAME_GAP
        )

        y = 35 + row * 190

        screen.blit(
            scaled_frame,
            (x, y),
        )

        label = font.render(
            str(index),
            True,
            (240, 240, 245),
        )

        label_rect = label.get_rect(
            center=(
                x + scaled_frame.get_width() // 2,
                y + scaled_frame.get_height() + 16,
            )
        )

        screen.blit(
            label,
            label_rect,
        )

    pygame.display.flip()

pygame.quit()
sys.exit()