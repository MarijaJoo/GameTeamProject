import pygame
import sys
import requests
import os
from game.classes import NPC

# =====================================================================
# 0. API КОНФИГУРАЦИЈА И НАЈАВА НА ИГРАЧ
# =====================================================================
API_URL = "http://127.0.0.1:8000"
player_id = 1
score = 0

print("=== Cyber Security Game ===")
username = input("Внесете го вашето корисничко име: ").strip()
if not username:
    username = "Gamer"

try:
    requests.post(f"{API_URL}/seed/")
    response = requests.post(f"{API_URL}/players/", json={"username": username, "score": 0})
    if response.status_code == 200:
        player_data = response.json()
        player_id = player_data["id"]
        score = player_data["score"]
        print(f" Успешно поврзување со API! Играч: {username} (ID: {player_id}, Поени: {score})")
    else:
        print("⚠️ API-то врати грешка. Играта ќе продолжи во офлајн мод.")
except Exception as e:
    print(f"❌ Не можев да се поврзам со API-то ({e}).\nИграта ќе продолжи во локален (офлајн) мод.")

# =====================================================================
# 1. ИНИЦИЈАЛИЗАЦИЈА НА PYGAME И ЗВУЦИ
# =====================================================================
pygame.init()
pygame.mixer.init()  # Иницијализација на модулот за звук

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cyber Security - Авантура за безбеден интернет")

# Бои
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
BLUE = (0, 100, 255)
RED = (220, 20, 20)
DARK_RED = (180, 0, 0)
GREEN = (20, 200, 20)
DARK_GREEN = (0, 150, 0)
HOVER_COLOR = (220, 220, 240)
OVERLAY_COLOR = (0, 0, 0, 150)

# Фонтови
font = pygame.font.SysFont('arial', 20)
title_font = pygame.font.SysFont('arial', 28, bold=True)

# Вчитување на звуци (Опционално: стави correct.wav и wrong.wav во assets)
try:
    sound_correct = pygame.mixer.Sound("assets/audio/sfx/correct.wav")
    sound_wrong = pygame.mixer.Sound("assets/audio/sfx/wrong.wav")
except:
    sound_correct = None
    sound_wrong = None


def remove_white_background(image, tolerance=240):
    image = image.convert_alpha()
    width, height = image.get_size()
    for x in range(width):
        for y in range(height):
            r, g, b, a = image.get_at((x, y))
            if r >= tolerance and g >= tolerance and b >= tolerance:
                image.set_at((x, y), (0, 0, 0, 0))
    return image


# --- ВЧИТУВАЊЕ СЛИКИ ---
player_img = pygame.image.load("assets/player.png").convert_alpha()
player_img.set_colorkey((111, 195, 223))
player_img = remove_white_background(player_img, tolerance=230)
player_img = pygame.transform.scale(player_img, (40, 40))

raw_npc_img = pygame.image.load("assets/npc.png").convert_alpha()
npc_img = remove_white_background(raw_npc_img, tolerance=220)
npc_img = pygame.transform.scale(npc_img, (45, 45))

raw_animal_img = pygame.image.load("assets/animal.png").convert_alpha()
animal_img = remove_white_background(raw_animal_img, tolerance=240)
animal_img = pygame.transform.scale(animal_img, (100, 100))  # Малку поголемо животинче

street_img = pygame.image.load("assets/street.png").convert()
street_img = pygame.transform.scale(street_img, (WIDTH, HEIGHT))

# Глобални променливи
player_rect = pygame.Rect(380, 510, 40, 40)
player_speed = 5
bg_x = 0
score_box_color = DARK_GREEN
npcs = []
current_npc = None

# Копчиња
btn1_rect = pygame.Rect(80, 400, 640, 35)
btn2_rect = pygame.Rect(80, 445, 640, 35)
btn_yes_rect = pygame.Rect(250, 350, 120, 40)
btn_no_rect = pygame.Rect(430, 350, 120, 40)
btn_play_again = pygame.Rect(180, 360, 220, 45)
btn_exit_game = pygame.Rect(420, 360, 200, 45)
quit_btn_rect = pygame.Rect(650, 10, 140, 40)


# НОВА ФУНКЦИЈА: Го прекршува текстот во повеќе редови за да не излезе од екранот
def draw_text_wrapped(surface, text, color, x, y, max_width, font):
    words = text.split(' ')
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (x, y + (i * font.get_linesize())))


# =====================================================================
# 2. ФУНКЦИЈА ЗА СТАРТУВАЊЕ / РЕСТАРТИРАЊЕ
# =====================================================================
def reset_game():
    global player_rect, score, npcs, current_npc, game_state, score_box_color, bg_x
    player_rect.x = 380
    player_rect.y = 510
    bg_x = 0
    score_box_color = DARK_GREEN
    current_npc = None
    game_state = "PLAYING"

    try:
        requests.post(f"{API_URL}/players/{player_id}/reset/")
        score = 0
    except Exception as e:
        print(f"Грешка при ресетирање на прогресот: {e}")

    loaded_npcs = []

    try:
        response = requests.get(f"{API_URL}/scenarios/")
        if response.status_code == 200:
            scenarios = response.json()
            for i, sc in enumerate(scenarios):
                x_pos = 600 + i * 550
                y_pos = 510 + (i % 3) * 5
                actions = sc["actions"]
                ans1 = actions[0]["action_text"] if len(actions) > 0 else "Опција 1"
                ans2 = actions[1]["action_text"] if len(actions) > 1 else "Опција 2"

                correct_choice = 1
                fb_correct = "Точно!"
                fb_wrong = "Грешка!"

                for idx, action in enumerate(actions):
                    if action["is_correct"]:
                        correct_choice = idx + 1
                        fb_correct = action["animal_message"]
                    else:
                        fb_wrong = action["animal_message"]

                npc = NPC(x_pos, y_pos, sc["npc_name"], sc["description"], ans1, ans2, correct_choice, fb_correct,
                          fb_wrong)
                npc.scenario_id = sc["id"]
                npc.action1_id = actions[0]["id"] if len(actions) > 0 else None
                npc.action2_id = actions[1]["id"] if len(actions) > 1 else None

                loaded_npcs.append(npc)
            return loaded_npcs
    except Exception as e:
        print(f"Грешка со API, вчитани се локалните резервни податоци: {e}")

    return []


# =====================================================================
# 3. ИСПРАЌАЊЕ ИЗБОР ДО API И ДОБИВАЊЕ ОДГОВОР
# =====================================================================
def submit_answer(chosen):
    global game_state, score, score_box_color, feedback_color, feedback_message
    game_state = "FEEDBACK"

    if not hasattr(current_npc, "scenario_id"):
        return  # Fallback за офлајн мод

    action_id = current_npc.action1_id if chosen == 1 else current_npc.action2_id
    payload = {
        "player_id": player_id,
        "scenario_id": current_npc.scenario_id,
        "action_id": action_id
    }

    try:
        res = requests.post(f"{API_URL}/progress/", json=payload)
        if res.status_code == 200:
            data = res.json()
            score = data["new_score"]
            feedback_message = data["animal_message"]

            if data["is_correct"]:
                feedback_color = GREEN
                score_box_color = DARK_GREEN
                if sound_correct: sound_correct.play()  # Пушти звук за точно!
            else:
                feedback_color = RED
                score_box_color = RED
                if sound_wrong: sound_wrong.play()  # Пушти звук за грешка!
        else:
            feedback_message = res.json().get("detail", "Грешка при зачувување!")
            feedback_color = RED
            score_box_color = RED
    except Exception as e:
        print(f"Проблем при испраќање до API: {e}")


# Иницијализирање
npcs = reset_game()
game_state = "START"
previous_state = "PLAYING"
feedback_message = ""
feedback_color = BLACK
clock = pygame.time.Clock()

# =====================================================================
# 4. ГЛАВНА ЈАМКА НА ИГРАТА
# =====================================================================
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
            elif game_state == "START" and event.key == pygame.K_SPACE:
                game_state = "PLAYING"
            elif game_state == "DIALOGUE":
                if event.key == pygame.K_1:
                    submit_answer(1)
                elif event.key == pygame.K_2:
                    submit_answer(2)
            elif game_state == "FEEDBACK" and event.key == pygame.K_SPACE:
                if current_npc in npcs: npcs.remove(current_npc)
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
                    pygame.quit()
                    sys.exit()
            elif game_state in ["PLAYING", "DIALOGUE", "FEEDBACK"]:
                if quit_btn_rect.collidepoint(mouse_pos):
                    previous_state = game_state
                    game_state = "CONFIRM_EXIT"
            if game_state == "DIALOGUE":
                if btn1_rect.collidepoint(mouse_pos):
                    submit_answer(1)
                elif btn2_rect.collidepoint(mouse_pos):
                    submit_answer(2)
            elif game_state == "FEEDBACK":
                if current_npc in npcs: npcs.remove(current_npc)
                current_npc = None
                game_state = "END" if len(npcs) == 0 else "PLAYING"

    # --- ДВИЖЕЊЕ ---
    if game_state == "PLAYING":
        keys = pygame.key.get_pressed()
        scroll_speed = 0
        if keys[pygame.K_LEFT]: scroll_speed = player_speed
        if keys[pygame.K_RIGHT]: scroll_speed = -player_speed
        bg_x = (bg_x + scroll_speed) % WIDTH
        for npc in npcs: npc.rect.x += scroll_speed

        if keys[pygame.K_UP] and player_rect.top > 460: player_rect.y -= player_speed
        if keys[pygame.K_DOWN] and player_rect.bottom < HEIGHT: player_rect.y += player_speed

        for npc in npcs:
            if player_rect.colliderect(npc.rect):
                game_state = "DIALOGUE"
                current_npc = npc
                push_back = 30 if keys[pygame.K_RIGHT] else -30
                bg_x += push_back
                for n in npcs: n.rect.x += push_back
                break

    # --- ЦРТАЊЕ ---
    screen.blit(street_img, (bg_x - WIDTH, 0))
    screen.blit(street_img, (bg_x, 0))

    if game_state == "START":
        pygame.draw.rect(screen, WHITE, (100, 130, 600, 350))
        pygame.draw.rect(screen, BLUE, (100, 130, 600, 350), 5)
        texts = [
            "ДОБРЕДОЈДОВТЕ!", "", f"Најавен како играч: {username}",
            "Движи се со стрелките на тастатурата.",
            "Избери одговор со кликнување или со 1 и 2.",
            "Притисни SPACE за почеток!"
        ]
        for i, t in enumerate(texts): screen.blit(font.render(t, True, BLACK), (120, 150 + i * 40))

    elif game_state in ["END", "FORCED_END"]:
        pygame.draw.rect(screen, WHITE, (100, 160, 600, 280))
        color = GREEN if game_state == "END" else RED
        pygame.draw.rect(screen, color, (100, 160, 600, 280), 5)
        screen.blit(title_font.render(f"Резултат: {score} поени", True, BLACK), (250, 200))
        pygame.draw.rect(screen, HOVER_COLOR if btn_play_again.collidepoint(mouse_pos) else WHITE, btn_play_again)
        pygame.draw.rect(screen, GREEN, btn_play_again, 2)
        screen.blit(font.render("ИГРАЈ ПОВТОРНО", True, DARK_GREEN), (210, 372))
        pygame.draw.rect(screen, HOVER_COLOR if btn_exit_game.collidepoint(mouse_pos) else WHITE, btn_exit_game)
        pygame.draw.rect(screen, RED, btn_exit_game, 2)
        screen.blit(font.render("ИЗЛЕЗ", True, DARK_RED), (490, 372))

    else:
        for npc in npcs: screen.blit(npc_img, npc.rect)
        screen.blit(player_img, player_rect)

        # Поени (синхронизирани со API)
        pygame.draw.rect(screen, WHITE, (10, 10, 150, 40), border_radius=20)
        pygame.draw.rect(screen, score_box_color, (10, 10, 150, 40), 3, border_radius=20)
        screen.blit(font.render(f"Поени: {score}", True, score_box_color), (30, 18))

        pygame.draw.rect(screen, WHITE, quit_btn_rect, border_radius=10)
        pygame.draw.rect(screen, RED, quit_btn_rect, 2, border_radius=10)
        screen.blit(font.render("ИЗЛЕЗ (ESC)", True, RED), (665, 18))

        if game_state == "DIALOGUE" and current_npc:
            pygame.draw.rect(screen, WHITE, (50, 80, 700, 440))
            pygame.draw.rect(screen, BLUE, (50, 80, 700, 440), 4)
            screen.blit(title_font.render(current_npc.name, True, BLACK), (80, 100))

            # Текстот на прашањето сега се крши автоматски
            draw_text_wrapped(screen, current_npc.question, RED, 80, 150, 640, font)

            for i, rect in enumerate([btn1_rect, btn2_rect]):
                color = HOVER_COLOR if rect.collidepoint(mouse_pos) else WHITE
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, BLACK, rect, 2)
                text = current_npc.ans1 if i == 0 else current_npc.ans2
                screen.blit(font.render(text, True, BLACK), (90, rect.y + 6))

        elif game_state == "FEEDBACK" and current_npc:
            # ГОЛЕМ POPUP ЗА ЖИВОТИНЧЕТО И ПОРАКАТА
            pygame.draw.rect(screen, WHITE, (40, 150, 720, 250))
            screen.blit(animal_img, (60, 200))  # Позиција на животинчето
            pygame.draw.rect(screen, feedback_color, (40, 150, 720, 250), 6)

            naslov = "ТОЧНО! (+10)" if feedback_color == GREEN else "ГРЕШКА! (-5)"
            screen.blit(title_font.render(naslov, True, feedback_color), (180, 170))

            # Ја користиме новата функција за текстот да не излезе од екранот!
            draw_text_wrapped(screen, feedback_message, BLACK, 180, 230, 550, font)

            screen.blit(font.render("Притисни SPACE или кликни за продолжување...", True, GRAY), (180, 360))

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
            screen.blit(font.render("НЕ", True, DARK_GREEN), (475, 358))

    pygame.display.flip()
    clock.tick(60)