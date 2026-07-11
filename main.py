import pygame
import sys

# 1. Иницијализација
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cyber Security - Авантура за безбеден интернет")

# Бои
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
ROAD_COLOR = (70, 70, 70)
SIDEWALK_COLOR = (180, 180, 180)
GRASS_COLOR = (34, 139, 34)
LINE_COLOR = (255, 255, 255)
BLUE = (0, 100, 255)
RED = (220, 20, 20)
DARK_RED = (180, 0, 0)
GREEN = (20, 200, 20)
DARK_GREEN = (0, 150, 0)
YELLOW = (255, 200, 0)
HOVER_COLOR = (220, 220, 240)
OVERLAY_COLOR = (0, 0, 0, 150)

# Фонтови
font = pygame.font.SysFont('arial', 20)
title_font = pygame.font.SysFont('arial', 28, bold=True)


# Класа за NPC
class NPC:
    def __init__(self, x, y, name, question, ans1, ans2, correct_choice, fb_correct, fb_wrong):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.name = name
        self.question = question
        self.ans1 = ans1
        self.ans2 = ans2
        self.correct_choice = correct_choice
        self.fb_correct = fb_correct
        self.fb_wrong = fb_wrong


# Глобални променливи
player_rect = pygame.Rect(380, 520, 40, 40)
player_speed = 5
score = 0
score_box_color = DARK_GREEN  # Почетна боја на поените
npcs = []
current_npc = None

# Копчиња
btn1_rect = pygame.Rect(60, 480, 680, 35)
btn2_rect = pygame.Rect(60, 520, 680, 35)
btn_yes_rect = pygame.Rect(250, 350, 120, 40)
btn_no_rect = pygame.Rect(430, 350, 120, 40)
btn_play_again = pygame.Rect(180, 360, 220, 45)
btn_exit_game = pygame.Rect(420, 360, 200, 45)
quit_btn_rect = pygame.Rect(650, 10, 140, 40)  # Постојано копче за излез


def reset_game():
    global player_rect, score, npcs, current_npc, game_state, score_box_color
    player_rect.x = 380
    player_rect.y = 520
    score = 0
    score_box_color = DARK_GREEN
    current_npc = None
    game_state = "PLAYING"

    npcs = [
        NPC(120, 80, "Непознат Гејмер", "Дај ми ја лозинката за 10,000 V-Bucks!", "1. Дај му ја лозинката",
            "2. Блокирај го", 2, "Браво! Никогаш не ја давај лозинката.", "Не! Хакерот ти го украде профилот."),
        NPC(640, 150, "Чуден Профил", "Кликни на линков http://super-igri.com за игра!", "1. Кликни", "2. Игнорирај", 2,
            "Супер! Непознати линкови се вирус.", "О-оу! Кликна на вирус."),
        NPC(120, 250, "Нов Пријател", "Каде живееш?", "1. Не кажувај", "2. Кажи му", 1,
            "Одлично! Не споделуваме лични податоци.", "Грешка! Опасно е да кажуваш каде живееш."),
        NPC(640, 330, "Лут Играч", "Ти си слаб!", "1. Врати навреди", "2. Пријави го", 2,
            "Одлично! Пријавувањето е најдобра одбрана.", "Грешка. Само пријави и блокирај."),
        NPC(120, 420, "Лажен Профил", "Прати ми твоја слика!", "1. Прати слика", "2. Прашај го во школо", 2,
            "Браво! Не праќај слики на непознати.", "Опасно! Не праќај слики без сигурност."),
        NPC(640, 500, "Хакер", "Симни мод за Minecraft!", "1. Симни веднаш", "2. Не, вирус е", 2,
            "Точно! Лажните модови се вируси.", "Лошо. Твојот компјутер има вирус.")
    ]
    return npcs


npcs = reset_game()
game_state = "START"
previous_state = "PLAYING"
feedback_message = ""
feedback_color = BLACK

clock = pygame.time.Clock()

# --- ГЛАВНА ЈАМКА ---
while True:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state in ["PLAYING", "DIALOGUE", "FEEDBACK"]:
                    previous_state = game_state
                    game_state = "CONFIRM_EXIT"
                elif game_state == "CONFIRM_EXIT":
                    game_state = previous_state
                elif game_state in ["START", "END", "FORCED_END"]:
                    pygame.quit()
                    sys.exit()

            elif game_state == "START" and event.key == pygame.K_SPACE:
                game_state = "PLAYING"
            elif game_state == "DIALOGUE":
                if event.key == pygame.K_1 or event.key == pygame.K_2:
                    chosen = 1 if event.key == pygame.K_1 else 2
                    game_state = "FEEDBACK"
                    if chosen == current_npc.correct_choice:
                        feedback_color = GREEN
                        feedback_message = current_npc.fb_correct
                        score += 10
                        score_box_color = DARK_GREEN  # Точен - зелено
                    else:
                        feedback_color = RED
                        feedback_message = current_npc.fb_wrong
                        score -= 5
                        if score < 0: score = 0
                        score_box_color = RED  # Грешка - црвено
            elif game_state == "FEEDBACK" and event.key == pygame.K_SPACE:
                npcs.remove(current_npc)
                current_npc = None
                game_state = "END" if len(npcs) == 0 else "PLAYING"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == "START":
                game_state = "PLAYING"
            elif game_state == "CONFIRM_EXIT":
                if btn_yes_rect.collidepoint(mouse_pos):
                    game_state = "FORCED_END"
                elif btn_no_rect.collidepoint(mouse_pos):
                    game_state = previous_state
            elif game_state in ["END", "FORCED_END"]:
                if btn_play_again.collidepoint(mouse_pos):
                    npcs = reset_game()
                elif btn_exit_game.collidepoint(mouse_pos):
                    pygame.quit(); sys.exit()
            elif game_state in ["PLAYING", "DIALOGUE", "FEEDBACK"]:
                if quit_btn_rect.collidepoint(mouse_pos):  # Клик на копчето ИЗЛЕЗ
                    previous_state = game_state
                    game_state = "CONFIRM_EXIT"

            if game_state == "DIALOGUE":
                chosen = 0
                if btn1_rect.collidepoint(mouse_pos):
                    chosen = 1
                elif btn2_rect.collidepoint(mouse_pos):
                    chosen = 2
                if chosen != 0:
                    game_state = "FEEDBACK"
                    if chosen == current_npc.correct_choice:
                        feedback_color = GREEN
                        feedback_message = current_npc.fb_correct
                        score += 10
                        score_box_color = DARK_GREEN
                    else:
                        feedback_color = RED
                        feedback_message = current_npc.fb_wrong
                        score -= 5
                        if score < 0: score = 0
                        score_box_color = RED
            elif game_state == "FEEDBACK":
                npcs.remove(current_npc)
                current_npc = None
                game_state = "END" if len(npcs) == 0 else "PLAYING"

    # --- ДВИЖЕЊЕ ---
    if game_state == "PLAYING":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.left > 0: player_rect.x -= player_speed
        if keys[pygame.K_RIGHT] and player_rect.right < WIDTH: player_rect.x += player_speed
        if keys[pygame.K_UP] and player_rect.top > 0: player_rect.y -= player_speed
        if keys[pygame.K_DOWN] and player_rect.bottom < HEIGHT: player_rect.y += player_speed
        for npc in npcs:
            if player_rect.colliderect(npc.rect):
                game_state = "DIALOGUE";
                current_npc = npc
                player_rect.x += 10 if player_rect.x < 400 else -10
                break

    # --- ЦРТАЊЕ ---
    screen.fill(GRASS_COLOR)
    pygame.draw.rect(screen, ROAD_COLOR, (200, 0, 400, HEIGHT))
    pygame.draw.rect(screen, SIDEWALK_COLOR, (100, 0, 80, HEIGHT))
    pygame.draw.rect(screen, SIDEWALK_COLOR, (620, 0, 80, HEIGHT))
    for y in range(0, HEIGHT, 60): pygame.draw.rect(screen, LINE_COLOR, (395, y, 10, 30))

    if game_state == "START":
        pygame.draw.rect(screen, WHITE, (100, 130, 600, 350))
        pygame.draw.rect(screen, BLUE, (100, 130, 600, 350), 5)
        texts = ["ДОБРЕДОЈДОВТЕ!", "", "Движи се со стрелки.", "Избери одговор 1 или 2.", "Притисни SPACE за почеток!"]
        for i, t in enumerate(texts): screen.blit(font.render(t, True, BLACK), (120, 150 + i * 40))

    elif game_state in ["END", "FORCED_END"]:
        pygame.draw.rect(screen, WHITE, (100, 160, 600, 280))
        color = GREEN if game_state == "END" else RED
        pygame.draw.rect(screen, color, (100, 160, 600, 280), 5)
        screen.blit(title_font.render(f"Резултат: {score} поени", True, BLACK), (250, 200))

        # Копчиња
        pygame.draw.rect(screen, HOVER_COLOR if btn_play_again.collidepoint(mouse_pos) else WHITE, btn_play_again)
        pygame.draw.rect(screen, GREEN, btn_play_again, 2)
        screen.blit(font.render("ИГРАЈ ПОВТОРНО", True, DARK_GREEN), (210, 370))

        pygame.draw.rect(screen, HOVER_COLOR if btn_exit_game.collidepoint(mouse_pos) else WHITE, btn_exit_game)
        pygame.draw.rect(screen, RED, btn_exit_game, 2)
        screen.blit(font.render("ИЗЛЕЗ", True, DARK_RED), (490, 370))

    else:
        for npc in npcs: pygame.draw.rect(screen, YELLOW, npc.rect)
        pygame.draw.rect(screen, BLUE, player_rect)

        # Поени (со променлива боја)
        pygame.draw.rect(screen, WHITE, (10, 10, 150, 40), border_radius=20)
        pygame.draw.rect(screen, score_box_color, (10, 10, 150, 40), 3, border_radius=20)
        screen.blit(font.render(f"Поени: {score}", True, score_box_color), (30, 18))

        # Копче за излез (постојано видливо)
        pygame.draw.rect(screen, WHITE, quit_btn_rect, border_radius=10)
        pygame.draw.rect(screen, RED, quit_btn_rect, 2, border_radius=10)
        screen.blit(font.render("ИЗЛЕЗ (ESC)", True, RED), (665, 18))

        if game_state == "DIALOGUE" and current_npc:
            pygame.draw.rect(screen, WHITE, (40, 400, 720, 180));
            pygame.draw.rect(screen, YELLOW, (40, 400, 720, 180), 4)
            screen.blit(title_font.render(f"{current_npc.name}:", True, BLACK), (60, 410))
            screen.blit(font.render(current_npc.question, True, RED), (60, 440))
            for i, rect in enumerate([btn1_rect, btn2_rect]):
                c = HOVER_COLOR if rect.collidepoint(mouse_pos) else WHITE
                pygame.draw.rect(screen, c, rect);
                pygame.draw.rect(screen, BLACK, rect, 1)
                txt = current_npc.ans1 if i == 0 else current_npc.ans2
                screen.blit(font.render(txt, True, BLACK), (65, 485 + (i * 40)))

        elif game_state == "FEEDBACK" and current_npc:
            pygame.draw.rect(screen, WHITE, (40, 200, 720, 200));
            pygame.draw.rect(screen, feedback_color, (40, 200, 720, 200), 4)
            screen.blit(title_font.render("ТОЧНО!" if feedback_color == GREEN else "ГРЕШКА!", True, feedback_color),
                        (60, 220))
            screen.blit(font.render(feedback_message, True, BLACK), (60, 280))
            screen.blit(font.render("Притисни SPACE...", True, GRAY), (60, 350))

        if game_state == "CONFIRM_EXIT":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA);
            overlay.fill(OVERLAY_COLOR);
            screen.blit(overlay, (0, 0))
            pygame.draw.rect(screen, WHITE, (200, 200, 400, 220));
            pygame.draw.rect(screen, RED, (200, 200, 400, 220), 4)
            screen.blit(title_font.render("Дали сигурно сакаш", True, BLACK), (270, 230));
            screen.blit(title_font.render("да излезеш?", True, BLACK), (320, 270))
            pygame.draw.rect(screen, HOVER_COLOR if btn_yes_rect.collidepoint(mouse_pos) else WHITE, btn_yes_rect);
            pygame.draw.rect(screen, RED, btn_yes_rect, 2);
            screen.blit(font.render("ДА", True, RED), (295, 358))
            pygame.draw.rect(screen, HOVER_COLOR if btn_no_rect.collidepoint(mouse_pos) else WHITE, btn_no_rect);
            pygame.draw.rect(screen, GREEN, btn_no_rect, 2);
            screen.blit(font.render("НЕ", True, DARK_GREEN), (475, 358))

    pygame.display.flip()
    clock.tick(60)