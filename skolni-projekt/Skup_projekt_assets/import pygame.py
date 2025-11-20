import pygame
import os
import json
import random

pygame.init()

# 1920x1080 main menu
screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("Main Menu")

clock = pygame.time.Clock()

# Colors and buttons
POZADI = (0, 170, 100)
GRAY = (200, 200, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)

button_width = 300
button_height = 80
button_spacing = 40
start_x = (1920 - button_width) // 2

group_height = 3 * button_height + 2 * button_spacing
start_y = int(1080 * 3 / 4 - group_height // 2)

# Main menu buttons
button0 = pygame.Rect(start_x - button_width - 40, start_y, button_width, button_height)  # New left button
button1 = pygame.Rect(start_x, start_y, button_width, button_height)  # Start
button2 = pygame.Rect(start_x, start_y + button_height + button_spacing, button_width, button_height)  # Options
button3 = pygame.Rect(start_x, start_y + 2 * (button_height + button_spacing), button_width, button_height)  # Exit
button4 = pygame.Rect(start_x + button_width + 40, start_y, button_width, button_height)  # Load Save
reset_button = pygame.Rect(start_x + button_width + 40, start_y + button_height + button_spacing, button_width, button_height)

# Start screen save button
save_button = pygame.Rect(20, 60, button_width, button_height)

# Options screen cheat button
cheat_button = pygame.Rect((1920 - button_width) // 2, (1080 - button_height) // 2, button_width, button_height)

# Background images
background_path = "D:/Projekt/menu.png"
background_image = pygame.image.load(background_path).convert()
background_image = pygame.transform.scale(background_image, (1920, 1080))

start_background_path = "D:/Projekt/herniPozadi.png"
start_background_image = pygame.image.load(start_background_path).convert()
start_background_image = pygame.transform.scale(start_background_image, (1920, 1080))

# Button images
button0_image = pygame.image.load("D:/Projekt/tutorial.png").convert_alpha()  # You need this image
button0_image = pygame.transform.scale(button0_image, (button_width, button_height))

button1_image = pygame.image.load("D:/Projekt/start.png").convert_alpha()
button1_image = pygame.transform.scale(button1_image, (button_width, button_height))
button2_image = pygame.image.load("D:/Projekt/options.png").convert_alpha()
button2_image = pygame.transform.scale(button2_image, (button_width, button_height))
button3_image = pygame.image.load("D:/Projekt/exit.png").convert_alpha()
button3_image = pygame.transform.scale(button3_image, (button_width, button_height))

# Load and Save button images
load_image = pygame.image.load("D:/Projekt/load.png").convert_alpha()
load_image = pygame.transform.scale(load_image, (button_width, button_height))
save_image = pygame.image.load("D:/Projekt/save.png").convert_alpha()
save_image = pygame.transform.scale(save_image, (button_width, button_height))

# Restart button image (for reset_button)
restart_image = pygame.image.load("D:/Projekt/restart.png").convert_alpha()
restart_image = pygame.transform.scale(restart_image, (button_width, button_height))

# Cheat button image
cheat_image = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
pygame.draw.rect(cheat_image, BLUE, (0, 0, button_width, button_height))
cheat_text = pygame.font.SysFont(None, 40).render("CHEAT MODE", True, WHITE)
cheat_image.blit(cheat_text, (button_width//2 - cheat_text.get_width()//2, button_height//2 - cheat_text.get_height()//2))

# Tile images - changed to use kytka1.png through kytka6.png
tile_images = [
    pygame.image.load("D:/Projekt/kytka1.png").convert_alpha(),
    pygame.image.load("D:/Projekt/kytka2.png").convert_alpha(),
    pygame.image.load("D:/Projekt/kytka3.png").convert_alpha(),
    pygame.image.load("D:/Projekt/kytka4.png").convert_alpha(),
    pygame.image.load("D:/Projekt/kytka5.png").convert_alpha(),
    pygame.image.load("D:/Projekt/kytka6.png").convert_alpha()
]

tile_size = 100
tile_images = [pygame.transform.scale(img, (tile_size, tile_size)) for img in tile_images]
tile_x = (1920 - tile_size) // 2
tile_y = (1080 - tile_size) // 2
tile_rects = [pygame.Rect(tile_x, tile_y, tile_size, tile_size) for _ in range(6)]  # Create rect for each flower

# Font
font = pygame.font.SysFont(None, 28)
esc_text = font.render("Press ESC to return to menu", True, BLACK)

# Left squares (modes) with logos
left_square_width = 80
left_square_height = 60
left_square_spacing = 20
left_group_height = 6 * left_square_height + 5 * left_square_spacing
left_start_y = (1080 - left_group_height) // 2
left_start_x = 50
left_squares = [pygame.Rect(left_start_x, left_start_y + i * (left_square_height + left_square_spacing),
                            left_square_width, left_square_height) for i in range(6)]

# Load logo images for the mode buttons
logo_images = []
for i in range(6):
    try:
        img = pygame.image.load(f"D:/Projekt/logo{i+1}.png").convert_alpha()
        img = pygame.transform.scale(img, (left_square_width, left_square_height))
        logo_images.append(img)
    except:
        # Fallback if logo image doesn't exist
        logo_images.append(None)

# Buy buttons next to each left square except the first
buy_button_width = button_width
buy_button_height = button_height
buy_button_spacing_y = left_square_height + left_square_spacing
buy_start_x = left_start_x + left_square_width + 20

buy_buttons = []
for i in range(1, 6):
    rect = pygame.Rect(buy_start_x, left_start_y + i * (left_square_height + left_square_spacing) - (left_square_height//2), 
                       50, 50)  # smaller squares, adjust size if you want
    buy_buttons.append(rect)

# Unlock requirements per mode (indexes 1-5, index 0 always unlocked)
unlock_costs = [0, 20, 30, 40, 50, 60]

# Amount added per mode on tile click
mode_adds = [1, 3, 8, 24, 69, 200]

# Mode state
modes_unlocked = [True, False, False, False, False, False]  # first mode unlocked by default
modes_uses = [float('inf'), 0, 0, 0, 0, 0]  # first mode infinite uses, others start at 0

# Track if buy buttons have cost deducted yet (per mode)
buy_first_time_used = [False, False, False, False, False, False]

# Cheat mode state
cheat_mode_active = False

save_path = "save.json"

def save_game():
    data = {
        'click_count': click_count,
        'modes_unlocked': modes_unlocked,
        'modes_uses': modes_uses,
        'buy_first_time_used': buy_first_time_used,
        'cheat_mode_active': cheat_mode_active,
    }
    with open(save_path, 'w') as f:
        json.dump(data, f)

def load_game():
    if os.path.exists(save_path):
        with open(save_path, 'r') as f:
            data = json.load(f)
            return data
    return None

def reset_save():
    if os.path.exists(save_path):
        os.remove(save_path)

current_screen = "menu"
click_count = 0
save_exists = os.path.exists(save_path)
current_mode = 0  # Default to first mode

def try_unlock_mode(mode_index):
    """Attempt to unlock the mode at mode_index (1 to 5)."""
    global click_count
    if modes_unlocked[mode_index]:
        return True  # already unlocked

    cost = unlock_costs[mode_index]
    if click_count >= cost:
        click_count -= cost
        modes_unlocked[mode_index] = True
        modes_uses[mode_index] = 0  # start with 0 uses unlocked
        buy_first_time_used[mode_index] = True
        return True
    return False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if current_screen == "menu":
                if button0.collidepoint(event.pos):
                    current_screen = "newpage"  # New page with herniPozadi.png
                elif button1.collidepoint(event.pos):  # Start - NEW GAME
                    click_count = 0
                    # Reset modes
                    modes_unlocked = [True, False, False, False, False, False]
                    modes_uses = [float('inf'), 0, 0, 0, 0, 0]
                    buy_first_time_used = [False, False, False, False, False, False]
                    cheat_mode_active = False
                    current_mode = 0  # default first mode
                    current_screen = "start"
                elif button2.collidepoint(event.pos):
                    current_screen = "options"
                elif button3.collidepoint(event.pos):
                    running = False
                elif button4.collidepoint(event.pos):  # Load Save
                    loaded = load_game()
                    if loaded:
                        click_count = loaded.get('click_count', 0)
                        modes_unlocked = loaded.get('modes_unlocked', [True, False, False, False, False, False])
                        modes_uses = loaded.get('modes_uses', [float('inf'), 0, 0, 0, 0, 0])
                        buy_first_time_used = loaded.get('buy_first_time_used', [False, False, False, False, False, False])
                        cheat_mode_active = loaded.get('cheat_mode_active', False)
                    else:
                        click_count = 0
                        modes_unlocked = [True, False, False, False, False, False]
                        modes_uses = [float('inf'), 0, 0, 0, 0, 0]
                        buy_first_time_used = [False, False, False, False, False, False]
                        cheat_mode_active = False
                    current_mode = 0
                    current_screen = "start"
                elif reset_button.collidepoint(event.pos):
                    reset_save()
                    save_exists = False

            elif current_screen == "start":
                # Check if clicking one of the left squares to select mode
                for i, rect in enumerate(left_squares):
                    if rect.collidepoint(event.pos) and modes_unlocked[i]:
                        current_mode = i
                        break
                # Check buy buttons for modes 2 to 6
                for i, buy_rect in enumerate(buy_buttons, start=1):
                    if buy_rect.collidepoint(event.pos) and not modes_unlocked[i]:
                        # Try to unlock mode
                        if try_unlock_mode(i):
                            # print(f"Unlocked mode {i+1}!")
                            pass
                        break
                    elif buy_rect.collidepoint(event.pos) and modes_unlocked[i]:
                        # Mode unlocked; 15% chance add uses randomly 3-12
                        if random.random() < 0.15:
                            added_uses = random.randint(2, 12)
                            modes_uses[i] += added_uses

                # Check tile click (middle image) - now using the correct rect for each flower
                if tile_rects[current_mode].collidepoint(event.pos):  # Changed to use current_mode's rect
                    # Add clicks based on mode
                    if modes_unlocked[current_mode]:
                        if cheat_mode_active:
                            click_count += 1000000  # Changed to add 1,000,000 clicks when cheat mode is active
                        else:
                            add_amount = mode_adds[current_mode]
                            if current_mode == 0:
                                click_count += add_amount
                            else:
                                # Check uses left
                                if modes_uses[current_mode] > 0:
                                    click_count += add_amount
                                    modes_uses[current_mode] -= 1
                                else:
                                    # No uses left, no clicks added
                                    pass

                # Save button
                if save_button.collidepoint(event.pos):
                    save_game()
                    save_exists = True

            elif current_screen == "options":
                if cheat_button.collidepoint(event.pos):
                    cheat_mode_active = not cheat_mode_active  # Toggle cheat mode
                else:
                    # Back to menu on click anywhere else
                    current_screen = "menu"

            elif current_screen == "newpage":
                # Pressing buttons here if any (none defined)
                pass

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if current_screen in ["start", "options", "newpage"]:
                    current_screen = "menu"

    # Drawing

    if current_screen == "menu":
        screen.fill(POZADI)
        screen.blit(background_image, (0, 0))

        # Draw buttons with images
        screen.blit(button0_image, button0)
        screen.blit(button1_image, button1)
        screen.blit(button2_image, button2)
        screen.blit(button3_image, button3)

        if save_exists:
            screen.blit(load_image, button4)
            screen.blit(restart_image, reset_button)
        else:
            # Disabled load and reset if no save
            pygame.draw.rect(screen, (100, 100, 100), button4)
            pygame.draw.rect(screen, (100, 100, 100), reset_button)

    elif current_screen == "start":
        screen.fill(WHITE)
        screen.blit(start_background_image, (0, 0))

        # Draw left squares with logos
        for i, rect in enumerate(left_squares):
            color = GREEN if modes_unlocked[i] else RED
            pygame.draw.rect(screen, color, rect)
            
            # Draw logo if available
            if logo_images[i] is not None:
                screen.blit(logo_images[i], rect)
            else:
                # Fallback: Write mode number inside
                mode_num_text = font.render(str(i+1), True, BLACK)
                screen.blit(mode_num_text, (rect.x + rect.width//2 - mode_num_text.get_width()//2,
                                            rect.y + rect.height//2 - mode_num_text.get_height()//2))

        # Draw buy buttons next to locked squares
        for i, buy_rect in enumerate(buy_buttons, start=1):
            if not modes_unlocked[i]:
                # Show cost text
                pygame.draw.rect(screen, RED, buy_rect)
                cost_text = font.render(str(unlock_costs[i]), True, WHITE)
                screen.blit(cost_text, (buy_rect.x + buy_rect.width // 2 - cost_text.get_width() // 2,
                                        buy_rect.y + buy_rect.height // 2 - cost_text.get_height() // 2))
            else:
                # Unlocked; show "uses" count and a green square buy button
                pygame.draw.rect(screen, GREEN, buy_rect)
                uses_text = font.render(str(int(modes_uses[i])), True, BLACK)
                screen.blit(uses_text, (buy_rect.x + buy_rect.width // 2 - uses_text.get_width() // 2,
                                        buy_rect.y + buy_rect.height // 2 - uses_text.get_height() // 2))

        # Draw tile (middle image) based on current mode - now showing kytka1.png through kytka6.png
        screen.blit(tile_images[current_mode], tile_rects[current_mode])  # Changed to use current_mode's rect

        # Draw clicks counter top left
        clicks_text = font.render(f"Clicks: {int(click_count)}", True, BLACK)
        screen.blit(clicks_text, (20, 20))

        # Draw selected mode info top right
        mode_info = f"Mode: {current_mode+1} (Adds {mode_adds[current_mode]} clicks)"
        screen.blit(font.render(mode_info, True, BLACK), (1920 - 450, 20))

        # Draw cheat mode indicator if active
        if cheat_mode_active:
            cheat_indicator = font.render("CHEAT MODE ACTIVE", True, RED)
            screen.blit(cheat_indicator, (1920 - cheat_indicator.get_width() - 20, 60))

        # Draw ESC hint bottom right
        screen.blit(esc_text, (1920 - esc_text.get_width() - 20, 1080 - esc_text.get_height() - 20))

        # Draw Save button bottom left
        pygame.draw.rect(screen, GRAY, save_button)
        screen.blit(save_image, save_button)

    elif current_screen == "options":
        screen.fill(WHITE)
        screen.blit(start_background_image, (0, 0))
        
        # Draw cheat mode button
        if cheat_mode_active:
            pygame.draw.rect(screen, GREEN, cheat_button)
        else:
            pygame.draw.rect(screen, RED, cheat_button)
        screen.blit(cheat_image, cheat_button)
        
        # Draw cheat mode status text
        status_text = font.render(f"Cheat Mode: {'ON' if cheat_mode_active else 'OFF'}", True, BLACK)
        screen.blit(status_text, (cheat_button.x + cheat_button.width//2 - status_text.get_width()//2, 
                                 cheat_button.y - 50))
        
        # Draw instructions
        instructions = [
            "Click the button to toggle cheat mode",
            "When active, each click gives 1,000,000 clicks",  # Updated this line
            "Click anywhere else to return to menu"
        ]
        for i, line in enumerate(instructions):
            text = font.render(line, True, BLACK)
            screen.blit(text, (cheat_button.x + cheat_button.width//2 - text.get_width()//2, 
                              cheat_button.y + cheat_button.height + 30 + i * 30))

        # Draw ESC hint bottom right
        screen.blit(esc_text, (1920 - esc_text.get_width() - 20, 1080 - esc_text.get_height() - 20))

    elif current_screen == "newpage":
        screen.fill(WHITE)
        screen.blit(start_background_image, (0, 0))
        screen.blit(esc_text, (1920 - esc_text.get_width() - 20, 1080 - esc_text.get_height() - 20))
        
        # Create a semi-transparent overlay for better text readability
        overlay = pygame.Surface((1600, 800), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Black with 50% transparency
        screen.blit(overlay, (160, 140))
        
        # Define the tutorial text
        tutorial_text = [
            "Tvá minulost má těžké boty a její kroky se neúprosně blíží.",
            "Dlužíš peníze lidem, kteří nezapomínají. Jedinou nadějí je útěk –",
            "zmizet daleko od města, na zapomenutý venkov, kde tě nikdo nezná.",
            "",
            "Našel jsi útočiště na staré, zanedbané farmě. Je to tvá šance na",
            "nový začátek, ale i tvá největší výzva. Nevíš, jestli máš víc času,",
            "nebo dluhů. Doufáš, že tě tu stíny minulosti nenajdou, ale co když ano?",
            "Musíš být připraven. Farma ti může poskytnout obživu i peníze na",
            "splacení alespoň části dluhu.",
            "",
            "Jenže začátky jsou těžké a půda sama o sobě nestačí. Čest jsi nechal",
            "ve městě. Aby sis zachránil kůži, budeš muset sáhnout k činům,",
            "na které nejsi hrdý. Ruka, která sází semínka, se bude muset",
            "naučit i krást.",
            "",
            "Jak daleko jsi ochoten zajít, abys vykoupil svou svobodu?"
        ]
        
        # Render each line of text
        tutorial_font = pygame.font.SysFont(None, 36)
        for i, line in enumerate(tutorial_text):
            text_surface = tutorial_font.render(line, True, WHITE)
            screen.blit(text_surface, (200, 200 + i * 40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()