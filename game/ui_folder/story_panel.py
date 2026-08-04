import pygame

from game.adventure.settings import (
    ANSWER_BORDER_COLOR,
    ANSWER_BOX_COLOR,
    OVERLAY_COLOR,
    POPUP_BORDER,
    POPUP_COLOR,
    SUBTEXT_COLOR,
    TEXT_COLOR,
)

from game.ui_folder.text import draw_wrapped_text


class StoryPanel:
    def __init__(self, title_font, body_font):
        self.title_font = title_font
        self.body_font = body_font

    def _create_panel(self, screen):
        overlay = pygame.Surface(
            screen.get_size(),
            pygame.SRCALPHA,
        )
        overlay.fill(OVERLAY_COLOR)
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(
            110,
            80,
            screen.get_width() - 220,
            screen.get_height() - 160,
        )

        pygame.draw.rect(
            screen,
            POPUP_COLOR,
            panel,
            border_radius=14,
        )

        pygame.draw.rect(
            screen,
            POPUP_BORDER,
            panel,
            3,
            border_radius=14,
        )

        return panel

    def draw(self, screen, engine):
        step = engine.current_step

        if not step:
            return

        if engine.showing_clue_feedback:
            self.draw_clue_feedback(screen, engine)
            return

        if step["type"] == "dialogue":
            self.draw_dialogue(screen, step)

        elif step["type"] == "clue":
            self.draw_clue(screen, step, engine)

        elif step["type"] == "final":
            self.draw_final_decision(
                screen,
                step,
                engine,
            )

    def draw_dialogue(self, screen, step):
        panel = self._create_panel(screen)

        speaker = self.title_font.render(
            step["speaker"],
            True,
            POPUP_BORDER,
        )

        screen.blit(
            speaker,
            (panel.x + 40, panel.y + 40),
        )

        draw_wrapped_text(
            screen,
            step["text"],
            self.body_font,
            TEXT_COLOR,
            panel.x + 40,
            panel.y + 110,
            panel.width - 80,
            line_spacing=10,
        )

        instruction = self.body_font.render(
            "Press SPACE to continue",
            True,
            SUBTEXT_COLOR,
        )

        instruction_rect = instruction.get_rect(
            center=(panel.centerx, panel.bottom - 35),
        )

        screen.blit(instruction, instruction_rect)

    def draw_clue(self, screen, step, engine):
        panel = self._create_panel(screen)

        heading = self.title_font.render(
            (
                f"CLUE {engine.clues_answered + 1}"
            ),
            True,
            POPUP_BORDER,
        )

        heading_rect = heading.get_rect(
            center=(panel.centerx, panel.y + 45),
        )
        screen.blit(heading, heading_rect)

        y = draw_wrapped_text(
            screen,
            step["question"],
            self.body_font,
            TEXT_COLOR,
            panel.x + 40,
            panel.y + 100,
            panel.width - 80,
        )

        y += 25

        for index, answer in enumerate(step["answers"]):
            answer_box = pygame.Rect(
                panel.x + 45,
                y,
                panel.width - 90,
                72,
            )

            pygame.draw.rect(
                screen,
                ANSWER_BOX_COLOR,
                answer_box,
                border_radius=10,
            )

            pygame.draw.rect(
                screen,
                ANSWER_BORDER_COLOR,
                answer_box,
                2,
                border_radius=10,
            )

            draw_wrapped_text(
                screen,
                f"{index + 1}. {answer}",
                self.body_font,
                TEXT_COLOR,
                answer_box.x + 15,
                answer_box.y + 15,
                answer_box.width - 30,
            )

            y += 88

        instruction = self.body_font.render(
            "Press 1 or 2 to inspect the clue",
            True,
            SUBTEXT_COLOR,
        )

        instruction_rect = instruction.get_rect(
            center=(panel.centerx, panel.bottom - 30),
        )

        screen.blit(instruction, instruction_rect)

    def draw_clue_feedback(self, screen, engine):
        panel = self._create_panel(screen)

        color = (
            (65, 200, 120)
            if engine.feedback_correct
            else (220, 80, 90)
        )

        heading = self.title_font.render(
            (
                "GOOD OBSERVATION!"
                if engine.feedback_correct
                else "LOOK MORE CAREFULLY"
            ),
            True,
            color,
        )

        heading_rect = heading.get_rect(
            center=(panel.centerx, panel.y + 60),
        )

        screen.blit(heading, heading_rect)

        draw_wrapped_text(
            screen,
            engine.feedback_message,
            self.body_font,
            TEXT_COLOR,
            panel.x + 45,
            panel.y + 135,
            panel.width - 90,
        )

        instruction = self.body_font.render(
            "Press SPACE to continue",
            True,
            SUBTEXT_COLOR,
        )

        instruction_rect = instruction.get_rect(
            center=(panel.centerx, panel.bottom - 35),
        )

        screen.blit(instruction, instruction_rect)

    def draw_final_decision(self, screen, step, engine,):
        panel = self._create_panel(screen)

        heading = self.title_font.render(
            "FINAL DECISION",
            True,
            POPUP_BORDER,
        )

        heading_rect = heading.get_rect(
            center=(panel.centerx, panel.y + 45),
        )

        screen.blit(heading, heading_rect)

        y = draw_wrapped_text(
            screen,
            step["intro"],
            self.body_font,
            TEXT_COLOR,
            panel.x + 40,
            panel.y + 100,
            panel.width - 80,
        )

        y += 25

        final_answers = engine.script.get(
            "final_answers",
            []
        )

        for index, answer in enumerate(final_answers):
            answer_box = pygame.Rect(
                panel.x + 45,
                y,
                panel.width - 90,
                72,
            )

            pygame.draw.rect(
                screen,
                ANSWER_BOX_COLOR,
                answer_box,
                border_radius=10,
            )

            pygame.draw.rect(
                screen,
                ANSWER_BORDER_COLOR,
                answer_box,
                2,
                border_radius=10,
            )

            draw_wrapped_text(
                screen,
                f"{index + 1}. {answer}",
                self.body_font,
                TEXT_COLOR,
                answer_box.x + 15,
                answer_box.y + 15,
                answer_box.width - 30,
            )

            y += 88

        instruction = self.body_font.render(
            "Press 1 or 2 to make your final decision",
            True,
            SUBTEXT_COLOR,
        )

        instruction_rect = instruction.get_rect(
            center=(panel.centerx, panel.bottom - 30),
        )

        screen.blit(instruction, instruction_rect)