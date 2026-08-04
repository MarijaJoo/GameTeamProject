from dataclasses import dataclass

import pygame


@dataclass(frozen=True)
class GameFonts:
    title: pygame.font.Font
    body: pygame.font.Font
    hud: pygame.font.Font


def create_game_fonts() -> GameFonts:
    """
    Creates all fonts used by the game.

    Call this only after pygame.init().
    """
    return GameFonts(
        title=pygame.font.SysFont(
            "arial",
            34,
            bold=True,
        ),
        body=pygame.font.SysFont(
            "arial",
            24,
        ),
        hud=pygame.font.SysFont(
            "arial",
            26,
            bold=True,
        ),
    )