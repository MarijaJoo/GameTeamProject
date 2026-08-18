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


# ==========================================
# AUDIO / SOUND MANAGER
# ==========================================
class SoundManager:
    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.sounds = {}
        self.current_music = None
        self.load_sfx()

    def load_sfx(self):
        """ (.wav) """
        sfx_directory = ASSETS_DIRECTORY / "audio" / "sfx"

        sfx_files = {
            "correct": "correct.wav",
            "wrong": "wrong.wav",
        }

        for sound_name, filename in sfx_files.items():
            sound_path = sfx_directory / filename

            if not sound_path.exists():
                print(f"Missing sound asset: {sound_path}")
                continue

            try:
                sound = pygame.mixer.Sound(str(sound_path))
                sound.set_volume(1.0)
                self.sounds[sound_name] = sound
            except pygame.error as error:
                print(f"Could not load sound {sound_path}: {error}")

    def play_sfx(self, sound_name):
        sound = self.sounds.get(sound_name)
        if sound:
            sound.set_volume(1.0)
            sound.play()
        else:
            print(f"Missing SFX: '{sound_name}'")

    def play_music(self, music_filename, loop=-1, volume=0.25):
        if self.current_music == music_filename:
            return

        music_path = ASSETS_DIRECTORY / "audio" / "music" / music_filename

        if not music_path.exists():
            print(f"Missing music asset: {music_path}")
            return

        try:
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loop)
            self.current_music = music_filename
        except pygame.error as error:
            print(f"Could not play music {music_path}: {error}")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_music = None