from pathlib import Path

import pygame


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIRECTORY = PROJECT_ROOT / "assets"


def load_image(
    relative_path,
    size=None,
):
    """
    Loads a transparent image from the assets directory.

    Returns None when the file is missing or cannot be loaded.
    This allows the game to continue using placeholder graphics.
    """
    image_path = (
        ASSETS_DIRECTORY
        / relative_path
    )

    if not image_path.exists():
        print(
            f"Missing optional asset: "
            f"{image_path}"
        )
        return None

    try:
        image = pygame.image.load(
            str(image_path)
        ).convert_alpha()

        if size is not None:
            image = pygame.transform.scale(
                image,
                size,
            )

        return image

    except pygame.error as error:
        print(
            f"Could not load image "
            f"{image_path}: {error}"
        )
        return None


def load_animation(
    folder,
    filenames,
    size=None,
):
    """
    Loads several animation frames.

    Missing frames are skipped.
    """
    frames = []

    for filename in filenames:
        image = load_image(
            Path(folder) / filename,
            size,
        )

        if image is not None:
            frames.append(image)

    return frames


def load_sprite_sheet(
    relative_path,
):
    image_path = (
        ASSETS_DIRECTORY
        / relative_path
    )

    if not image_path.exists():
        print(
            f"Missing sprite sheet: {image_path}"
        )
        return None

    try:
        return pygame.image.load(
            str(image_path)
        ).convert_alpha()

    except pygame.error as error:
        print(
            f"Could not load sprite sheet "
            f"{image_path}: {error}"
        )
        return None