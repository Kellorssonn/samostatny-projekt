import pygame
import random
import time
import sys
import os

# ---------------------- TŘÍDY ----------------------

class Projectile:
    def __init__(self, x, y, pierce=False):
        self.rect = pygame.Rect(x, y - 5, 10, 10)
        self.speed = 10
        self.pierce = pierce

    def move(self):
        self.rect.x += self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 0), self.rect.center, 5)

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.base_speed = 5
        self.speed = 5
        self.projectiles = []
        self.last_shot_time = 0
        self.shoot_cooldown = 0.6

        # power-up efekty
        self.shield = False
        self.shield_end_time = 0
        self.shotgun = False
        self.shotgun_end_time = 0
        self.fast_shoot = False
        self.fast_shoot_end_time = 0
        self.fast_move = False
        self.fast_move_end_time = 0
        self.pierce = False
        self.pierce_end_time = 0

    def move(self, keys):
        if self.fast_move and time.time() > self.fast_move_end_time:
            self.fast_move = False
            self.speed = self.base_speed

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > 540:
            self.rect.bottom = 540

    def shoot(self):
        if self.fast_shoot and time.time() > self.fast_shoot_end_time:
            self.fast_shoot = False
            self.shoot_cooldown = 0.6

        current_time = time.time()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            if self.shotgun:
                for i in range(-2, 3):
                    proj = Projectile(self.rect.right, self.rect.centery + i*10, pierce=self.pierce)
                    self.projectiles.append(proj)
            else:
                proj = Projectile(self.rect.right, self.rect.centery, pierce=self.pierce)
                self.projectiles.append(proj)

            self.last_shot_time = current_time

    def update(self, screen):
        pygame.draw.rect(screen, (0, 255, 0), self.rect)
        for projectile in self.projectiles[:]:
            projectile.move()
            projectile.draw(screen)
            if projectile.rect.left > 960:
                self.projectiles.remove(projectile)

class Enemy:
    def __init__(self):
        self.image = pygame.image.load("sunflower.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = 960
        self.rect.y = random.randint(0, 540 - 40)
        self.speed = 3

    def move(self):
        self.rect.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class PowerUp:
    TYPES = ["shield", "shotgun", "speed", "quick", "pierce"]
    ICONS = {
        "shield": "shield.jpg",
        "shotgun": "shotgun.jpg",
        "speed": "speed.jpg",
        "quick": "quick.jpg",
        "pierce": "pierce.jpg"
    }

    def __init__(self):
        self.type = random.choice(self.TYPES)
        self.image = pygame.image.load(self.ICONS[self.type]).convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = 960
        self.rect.y = random.randint(0, 540 - 40)
        self.speed = 3

    def move(self):
        self.rect.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# ---------------------- HRA ----------------------

def game_window(highscore):
    pygame.init()
    screen = pygame.display.set_mode((960, 540))
    pygame.display.set_caption("Garden Defender")

    pozadi = pygame.image.load("herniPozadi.png").convert()
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 48)

    player = Player(100, 270)
    enemies = []
    powerups = []
    score = 0
    lives = 5
    spawn_time = time.time() + random.uniform(0.5, 1.5)
    next_powerup_spawn = time.time() + random.uniform(15, 20)

    running = True
    game_over = False
    game_over_time = 0

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    player.shoot()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    player.shoot()

        keys = pygame.key.get_pressed()
        if not game_over:
            player.move(keys)

        # spawn nepřátel
        if not game_over and time.time() >= spawn_time:
            enemies.append(Enemy())
            chance = 0.2
            while random.random() < chance:
                enemies.append(Enemy())
            spawn_time = time.time() + random.uniform(0.5, 1.5)

        # spawn powerupů
        if not game_over and time.time() >= next_powerup_spawn:
            powerups.append(PowerUp())
            next_powerup_spawn = time.time() + random.uniform(15, 20)

        screen.blit(pozadi, (0, 0))

        if not game_over:
            player.update(screen)

            # vykreslení životů
            for i in range(5):
                color = (0, 0, 0) if i < lives else (100, 100, 100)
                pygame.draw.circle(screen, color, (20 + i*30, 20), 10)

            # nepřátelé
            for enemy in enemies[:]:
                enemy.move()
                enemy.draw(screen)

                if enemy.rect.colliderect(player.rect):
                    if not player.shield:
                        lives -= 1
                    enemies.remove(enemy)
                elif enemy.rect.left <= 0:
                    if not player.shield:
                        lives -= 1
                    enemies.remove(enemy)

                for projectile in player.projectiles[:]:
                    if enemy.rect.colliderect(projectile.rect):
                        if not projectile.pierce:
                            enemies.remove(enemy)
                        try:
                            player.projectiles.remove(projectile)
                        except ValueError:
                            pass
                        score += 1
                        break

            # powerupy
            for pu in powerups[:]:
                pu.move()
                pu.draw(screen)
                if pu.rect.colliderect(player.rect):
                    powerups.remove(pu)
                    if pu.type == "shield":
                        player.shield = True
                        player.shield_end_time = time.time() + 5
                    elif pu.type == "shotgun":
                        player.shotgun = True
                        player.shotgun_end_time = time.time() + 5
                    elif pu.type == "speed":
                        player.fast_shoot = True
                        player.shoot_cooldown = 0.1
                        player.fast_shoot_end_time = time.time() + 5
                    elif pu.type == "quick":
                        player.fast_move = True
                        player.speed = 10
                        player.fast_move_end_time = time.time() + 5
                    elif pu.type == "pierce":
                        player.pierce = True
                        player.fast_shoot_end_time = time.time() + 5

            # konec efektů
            if player.shield and time.time() > player.shield_end_time:
                player.shield = False
            if player.shotgun and time.time() > player.shotgun_end_time:
                player.shotgun = False
            if player.fast_shoot and time.time() > player.fast_shoot_end_time:
                player.fast_shoot = False
                player.shoot_cooldown = 0.6
            if player.fast_move and time.time() > player.fast_move_end_time:
                player.fast_move = False
                player.speed = player.base_speed
            if player.pierce and time.time() > player.fast_shoot_end_time:
                player.pierce = False

            if lives <= 0:
                game_over = True
                game_over_time = time.time()

            # vykreslení skóre
            score_text = font.render(str(score), True, (255, 255, 255))
            screen.blit(score_text, (900, 10))

            # vykreslení aktuálního power-upu vlevo dole
            active_powerup = None
            if player.shield:
                active_powerup = "shield"
            elif player.shotgun:
                active_powerup = "shotgun"
            elif player.fast_shoot:
                active_powerup = "speed"
            elif player.fast_move:
                active_powerup = "quick"
            elif player.pierce:
                active_powerup = "pierce"

            if active_powerup:
                icon_path = PowerUp.ICONS[active_powerup]
                icon_image = pygame.image.load(icon_path).convert_alpha()
                icon_image = pygame.transform.scale(icon_image, (50, 50))
                screen.blit(icon_image, (20, 480))  # levý dolní roh

        else:
            over_text = font.render("GAME OVER", True, (255, 50, 50))
            text_rect = over_text.get_rect(center=(480, 220))
            screen.blit(over_text, text_rect)

            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(480, 270))
            screen.blit(score_text, score_rect)

            if score > highscore:
                highscore = score
                with open("highscore.txt", "w") as f:
                    f.write(str(highscore))

            if time.time() - game_over_time >= 5:
                running = False

        pygame.display.update()

    return highscore

# ---------------------- MENU ----------------------

def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((960, 540))
    pygame.display.set_caption("Garden Defender")

    pozadi = pygame.image.load("herniPozadi.png").convert()
    logo = pygame.image.load("logo.png").convert_alpha()
    start_button = pygame.image.load("start.png").convert_alpha()
    exit_button = pygame.image.load("exit.png").convert_alpha()
    font = pygame.font.Font(None, 40)

    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            try:
                highscore = int(f.read())
            except:
                highscore = 0
    else:
        highscore = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if start_rect.collidepoint(mouse_pos):
                    highscore = game_window(highscore)
                if exit_rect.collidepoint(mouse_pos):
                    running = False

        screen.blit(pozadi, (0, 0))
        screen.blit(logo, (213, 20))

        start_rect = start_button.get_rect(center=(960 // 2, 300))
        screen.blit(start_button, start_rect)

        exit_rect = exit_button.get_rect(center=(960 // 2, 380))
        screen.blit(exit_button, exit_rect)

        hs_text = font.render(f"Highscore: {highscore}", True, (255, 255, 255))
        hs_rect = hs_text.get_rect(center=(960 // 2, 350))
        screen.blit(hs_text, hs_rect)

        pygame.display.update()

    pygame.quit()

# ---------------------- SPUŠTĚNÍ ----------------------

if __name__ == "__main__":
    main_menu()
