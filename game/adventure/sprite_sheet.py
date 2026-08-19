import pygame


def slice_sprite_sheet(
    sheet,
    frame_width,
    frame_height,
):


    frames = []

    sheet_width = sheet.get_width()
    sheet_height = sheet.get_height()

    if sheet_height < frame_height:
        raise ValueError(
            "The sprite sheet is shorter than the requested frame height."
        )

    frame_count = sheet_width // frame_width

    for frame_index in range(frame_count):
        frame_rect = pygame.Rect(
            frame_index * frame_width,
            0,
            frame_width,
            frame_height,
        )

        frame = pygame.Surface(
            (frame_width, frame_height),
            pygame.SRCALPHA,
        )

        frame.blit(
            sheet,
            (0, 0),
            frame_rect,
        )

        frames.append(frame)

    return frames
