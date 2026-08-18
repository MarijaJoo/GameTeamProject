def wrap_text(text, font, max_width):
    words = text.split()

    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(
            current_line + [word]
        )

        if font.size(test_line)[0] <= max_width:
            current_line.append(word)

        else:
            if current_line:
                lines.append(
                    " ".join(current_line)
                )

            current_line = [word]

    if current_line:
        lines.append(
            " ".join(current_line)
        )

    return lines


def draw_wrapped_text(
    screen,
    text,
    font,
    color,
    x,
    y,
    max_width,
    line_spacing=6,
):
    lines = wrap_text(
        text,
        font,
        max_width,
    )

    for line in lines:
        rendered = font.render(
            line,
            True,
            color,
        )

        screen.blit(
            rendered,
            (x, y),
        )

        y += (
            font.get_linesize()
            + line_spacing
        )

    return y