import pygame

class NPC:
    def __init__(self, x, y, name, question, ans1, ans2,
                 correct_choice, fb_correct, fb_wrong):

        self.rect = pygame.Rect(x, y, 40, 40)
        self.name = name
        self.question = question
        self.ans1 = ans1
        self.ans2 = ans2
        self.correct_choice = correct_choice
        self.fb_correct = fb_correct
        self.fb_wrong = fb_wrong