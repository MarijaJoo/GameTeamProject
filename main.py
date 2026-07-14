import pygame
import sys
<<<<<<< HEAD
=======
from game.classes import NPC
>>>>>>> b48dba0bbf5f065632aac61bf23cca760aee7cf0

# 1. Иницијализација
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cyber Security - Авантура за безбеден интернет")

# Бои
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
<<<<<<< HEAD
ROAD_COLOR = (70, 70, 70)
SIDEWALK_COLOR = (180, 180, 180)
GRASS_COLOR = (34, 139, 34)
LINE_COLOR = (255, 255, 255)
=======
>>>>>>> b48dba0bbf5f065632aac61bf23cca760aee7cf0
BLUE = (0, 100, 255)
RED = (220, 20, 20)
DARK_RED = (180, 0, 0)
GREEN = (20, 200, 20)
DARK_GREEN = (0, 150, 0)
<<<<<<< HEAD
YELLOW = (255, 200, 0)
=======
>>>>>>> b48dba0bbf5f065632aac61bf23cca760aee7cf0
HOVER_COLOR = (220, 220, 240)
OVERLAY_COLOR = (0, 0, 0, 150)

# Фонтови
font = pygame.font.SysFont('arial', 20)
title_font = pygame.font.SysFont('arial', 28, bold=True)


<<<<<<< HEAD
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
=======
# --- ФУНКЦИЈА ЗА ЧИСТЕЊЕ НА БЕЛИТЕ И СВЕТЛИТЕ ПОЗАДИНИ СО ТОЛЕРАНЦИЈА ---
def remove_white_background(image, tolerance=240):
    """
    Ги зема сите пиксели што се посветли од одредена вредност (tolerance)
    и ги прави 100% проѕирни. Ова ги чисти сите бели и сивкави рабови!
    """
    image = image.convert_alpha()
    width, height = image.get_size()
    for x in range(width):
        for y in range(height):
            r, g, b, a = image.get_at((x, y))
            # Ако пикселот е многу блиску до бел (над вредноста на tolerance за сите три бои)
            if r >= tolerance and g >= tolerance and b >= tolerance:
                image.set_at((x, y), (0, 0, 0, 0))  # Прави го целосно проѕирен
    return image


# --- ВЧИТУВАЊЕ СЛИКИ И ЧИСТЕЊЕ НА ПОЗАДИНИТЕ ---

# 1. Играч (Бришење на сината позадина + чистење на белите рабови долу)
player_img = pygame.image.load("assets/player.png").convert_alpha()
player_img.set_colorkey((111, 195, 223))  # Прво ја трга сината боја
player_img = remove_white_background(player_img, tolerance=230)  # Го чисти белото под нозете
player_img = pygame.transform.scale(player_img, (40, 40))

# 2. NPC карактери (Целосно чистење на белата и сивкаста позадина/сенка околу нив)
raw_npc_img = pygame.image.load("assets/npc.png").convert_alpha()
npc_img = remove_white_background(raw_npc_img, tolerance=220)  # Толеранција за да ги снема и сенките
npc_img = pygame.transform.scale(npc_img, (45, 45))  # Малку зголемено за подобра видливост

# 3. Животно Ментор
raw_animal_img = pygame.image.load("assets/animal.png").convert_alpha()
animal_img = remove_white_background(raw_animal_img, tolerance=240)
animal_img = pygame.transform.scale(animal_img, (80, 80))

# 4. Позадина на улицата
street_img = pygame.image.load("assets/street.jpg").convert()
street_img = pygame.transform.scale(street_img, (WIDTH, HEIGHT))

# Глобални променливи за играта
player_rect = pygame.Rect(380, 510, 40, 40)
player_speed = 5

# Arka plan kaydırma değişkeni
bg_x = 0

score = 0
score_box_color = DARK_GREEN
>>>>>>> b48dba0bbf5f065632aac61bf23cca760aee7cf0
npcs = []
current_npc = None

# Копчиња
<<<<<<< HEAD
btn1_rect = pygame.Rect(60, 480, 680, 35)
btn2_rect = pygame.Rect(60, 520, 680, 35)
=======
btn1_rect = pygame.Rect(80, 400, 640, 35)
btn2_rect = pygame.Rect(80, 445, 640, 35)
message_box = pygame.Rect(80, 100, 640, 220)
>>>>>>> b48dba0bbf5f065632aac61bf23cca760aee7cf0
btn_yes_rect = pygame.Rect(250, 350, 120, 40)
btn_no_rect = pygame.Rect(430, 350, 120, 40)
btn_play_again = pygame.Rect(180, 360, 220, 45)
btn_exit_game = pygame.Rect(420, 360, 200, 45)
<<<<<<< HEAD
quit_btn_rect = pygame.Rect(650, 10, 140, 40)  # Постојано копче за излез


def reset_game():
    global player_rect, score, npcs, current_npc, game_state, score_box_color
    player_rect.x = 380
    player_rect.y = 520
=======
quit_btn_rect = pygame.Rect(650, 10, 140, 40)


def reset_game():
    global player_rect, score, npcs, current_npc, game_state, score_box_color, bg_x
    player_rect.x = 380
    player_rect.y = 510
    bg_x = 0
>>>>>>> b48dba0bbf5f065632aac61bf23cca760aee7cf0
    score = 0
    score_box_color = DARK_GREEN
    current_npc = None
    game_state = "PLAYING"

<<<<<<< HEAD
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
=======
    # Сите NPC карактери се поставени исклучиво на долниот дел (на патот/тротоарот)
    return [
        NPC(
            600, 510,
            "Сигурносен Асистент",
            "Ајде да направиме сигурна лозинка\nза твојот нов профил.",
            "1. Избери '123456'",
            "2. Избери 'Tiger!98'",
            2,
            "Одлично! Силните лозинки содржат букви, бројки и симболи.",
            "Премногу лесно! Оваа лозинка хакерите лесно ќе ја погодат."
        ),
        NPC(
            1100, 500,
            "Непознат Гејмер",
            "Здраво! Кажи ми ја твојата\nдомашна адреса за да ти пратам подарок.",
            "1. Не ја кажувај адресата",
            "2. Кажи му ја адресата",
            1,
            "Супер! Личните информации треба да останат твоја тајна.",
            "Никогаш не кажувај ја твојата адреса на непознати на интернет!"
        ),
        NPC(
            1600, 520,
            "Твојот Најдобар Другар",
            "Ти праќам чуден линк без порака.\n(Неговиот профил можеби е хакиран!)",
            "1. Отвори го линкот веднаш",
            "2. Прашај го дали навистина тој го пратил",
            2,
            "Паметно! Секогаш провери со пријателот пред да отвориш чуден линк.",
            "Внимавај! Профилот на твојот другар можеби бил хакиран."
        )
    ]
>>>>>>> b48dba0bbf5f065632aac61bf23cca760aee7cf0


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
<<<<<<< HEAD
                        score_box_color = DARK_GREEN  # Точен - зелено
=======
                        score_box_color = DARK_GREEN
>>>>>>> b48dba0bbf5f065632aac61bf23cca760aee7cf0
                    else:
                        feedback_color = RED
                        feedback_message = current_npc.fb_wrong
                        score -= 5
                        if score < 0: score = 0
<<<<<<< HEAD
                        score_box_color = RED  # Грешка - црвено
            elif game_state == "FEEDBACK" and event.key == pygame.K_SPACE:
                npcs.remove(current_npc)
=======
                        score_box_color = RED
            elif game_state == "FEEDBACK" and event.key == pygame.K_SPACE:
                if current_npc in npcs:
                    npcs.remove(current_npc)
>>>>>>> b48dba0bbf5f065632aac61bf23cca760aee7cf0
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
<<<<<<< HEAD
                    pygame.quit(); sys.exit()
            elif game_state in ["PLAYING", "DIALOGUE", "FEEDBACK"]:
                if quit_btn_rect.collidepoint(mouse_pos):  # Клик на копчето ИЗЛЕЗ
=======
                    pygame.quit();
                    sys.exit()
            elif game_state in ["PLAYING", "DIALOGUE", "FEEDBACK"]:
                if quit_btn_rect.collidepoint(mouse_pos):
>>>>>>> b48dba0bbf5f065632aac61bf23cca760aee7cf0
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
<<<<<<< HEAD
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
=======
                if current_npc in npcs:
                    npcs.remove(current_npc)
                current_npc = None
                game_state = "END" if len(npcs) == 0 else "PLAYING"

    # --- СЦЕНА И ДВИЖЕЊЕ ---
    if game_state == "PLAYING":
        keys = pygame.key.get_pressed()
        scroll_speed = 0

        # Се движи позадината, играчот останува во средина
        if keys[pygame.K_LEFT]:
            scroll_speed = player_speed
        if keys[pygame.K_RIGHT]:
            scroll_speed = -player_speed

        bg_x += scroll_speed
        bg_x %= WIDTH

        # Ги движиме и NPC-ата со сцената
        for npc in npcs:
            npc.rect.x += scroll_speed

        # Движење нагоре и надолу само на патот (Y: 460 - 550)
        if keys[pygame.K_UP] and player_rect.top > 460:
            player_rect.y -= player_speed
        if keys[pygame.K_DOWN] and player_rect.bottom < HEIGHT:
            player_rect.y += player_speed

        # Проверка за судир со NPC
        for npc in npcs:
            if player_rect.colliderect(npc.rect):
                game_state = "DIALOGUE"
                current_npc = npc
                # Мало оттурнување на камерата за да не се заглави дијалогот
                push_back = 30 if keys[pygame.K_RIGHT] else -30
                bg_x += push_back
                for n in npcs:
                    n.rect.x += push_back
                break

    # --- ЦРТАЊЕ ---

    # Бесконечен Луп на позадината
    screen.blit(street_img, (bg_x - WIDTH, 0))
    screen.blit(street_img, (bg_x, 0))
>>>>>>> b48dba0bbf5f065632aac61bf23cca760aee7cf0

    if game_state == "START":
        pygame.draw.rect(screen, WHITE, (100, 130, 600, 350))
        pygame.draw.rect(screen, BLUE, (100, 130, 600, 350), 5)
<<<<<<< HEAD
        texts = ["ДОБРЕДОЈДОВТЕ!", "", "Движи се со стрелки.", "Избери одговор 1 или 2.", "Притисни SPACE за почеток!"]
=======
        texts = ["ДОБРЕДОЈДОВТЕ!", "", "Движи се со стрелките на тастатурата (Лево/Десно за одење).",
                 "Избери одговор со кликнување или со 1 и 2.", "Притисни SPACE за почеток!"]
>>>>>>> b48dba0bbf5f065632aac61bf23cca760aee7cf0
        for i, t in enumerate(texts): screen.blit(font.render(t, True, BLACK), (120, 150 + i * 40))

    elif game_state in ["END", "FORCED_END"]:
        pygame.draw.rect(screen, WHITE, (100, 160, 600, 280))
        color = GREEN if game_state == "END" else RED
        pygame.draw.rect(screen, color, (100, 160, 600, 280), 5)
        screen.blit(title_font.render(f"Резултат: {score} поени", True, BLACK), (250, 200))

<<<<<<< HEAD
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
=======
        pygame.draw.rect(screen, HOVER_COLOR if btn_play_again.collidepoint(mouse_pos) else WHITE, btn_play_again)
        pygame.draw.rect(screen, GREEN, btn_play_again, 2)
        screen.blit(font.render("ИГРАЈ ПОВТОРНО", True, DARK_GREEN), (210, 372))

        pygame.draw.rect(screen, HOVER_COLOR if btn_exit_game.collidepoint(mouse_pos) else WHITE, btn_exit_game)
        pygame.draw.rect(screen, RED, btn_exit_game, 2)
        screen.blit(font.render("ИЗЛЕЗ", True, DARK_RED), (490, 372))

    else:
        # 1. Цртање на исчистените NPC ликови
        for npc in npcs:
            screen.blit(npc_img, npc.rect)

        # 2. Цртање на играчот (без никакви бели траги)
        screen.blit(player_img, player_rect)

        # Поени
>>>>>>> b48dba0bbf5f065632aac61bf23cca760aee7cf0
        pygame.draw.rect(screen, WHITE, (10, 10, 150, 40), border_radius=20)
        pygame.draw.rect(screen, score_box_color, (10, 10, 150, 40), 3, border_radius=20)
        screen.blit(font.render(f"Поени: {score}", True, score_box_color), (30, 18))

<<<<<<< HEAD
        # Копче за излез (постојано видливо)
=======
        # Излез копче
>>>>>>> b48dba0bbf5f065632aac61bf23cca760aee7cf0
        pygame.draw.rect(screen, WHITE, quit_btn_rect, border_radius=10)
        pygame.draw.rect(screen, RED, quit_btn_rect, 2, border_radius=10)
        screen.blit(font.render("ИЗЛЕЗ (ESC)", True, RED), (665, 18))

        if game_state == "DIALOGUE" and current_npc:
<<<<<<< HEAD
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
=======
            pygame.draw.rect(screen, WHITE, (50, 80, 700, 440))
            pygame.draw.rect(screen, BLUE, (50, 80, 700, 440), 4)

            screen.blit(title_font.render(current_npc.name, True, BLACK), (80, 100))

            lines = current_npc.question.split("\n")
            y = 150
            for line in lines:
                screen.blit(font.render(line, True, RED), (80, y))
                y += 30

            for i, rect in enumerate([btn1_rect, btn2_rect]):
                color = HOVER_COLOR if rect.collidepoint(mouse_pos) else WHITE
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, BLACK, rect, 2)
                text = current_npc.ans1 if i == 0 else current_npc.ans2
                screen.blit(font.render(text, True, BLACK), (90, rect.y + 6))

        elif game_state == "FEEDBACK" and current_npc:
            pygame.draw.rect(screen, WHITE, (40, 200, 720, 200))
            screen.blit(animal_img, (70, 260))
            pygame.draw.rect(screen, feedback_color, (40, 200, 720, 200), 4)
            screen.blit(title_font.render("ТОЧНО!" if feedback_color == GREEN else "ГРЕШКА!", True, feedback_color),
                        (170, 220))
            screen.blit(font.render(feedback_message, True, BLACK), (170, 280))
            screen.blit(font.render("Притисни SPACE или кликни за продолжување...", True, GRAY), (170, 340))

        if game_state == "CONFIRM_EXIT":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill(OVERLAY_COLOR)
            screen.blit(overlay, (0, 0))
            pygame.draw.rect(screen, WHITE, (200, 200, 400, 220))
            pygame.draw.rect(screen, RED, (200, 200, 400, 220), 4)
            screen.blit(title_font.render("Дали сигурно сакаш", True, BLACK), (270, 230))
            screen.blit(title_font.render("да излезеш?", True, BLACK), (320, 270))
            pygame.draw.rect(screen, HOVER_COLOR if btn_yes_rect.collidepoint(mouse_pos) else WHITE, btn_yes_rect)
            pygame.draw.rect(screen, RED, btn_yes_rect, 2)
            screen.blit(font.render("ДА", True, RED), (295, 358))
            pygame.draw.rect(screen, HOVER_COLOR if btn_no_rect.collidepoint(mouse_pos) else WHITE, btn_no_rect)
            pygame.draw.rect(screen, GREEN, btn_no_rect, 2)
>>>>>>> b48dba0bbf5f065632aac61bf23cca760aee7cf0
            screen.blit(font.render("НЕ", True, DARK_GREEN), (475, 358))

    pygame.display.flip()
    clock.tick(60)