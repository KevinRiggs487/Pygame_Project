import pygame  
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Impact Clone")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Clock and FPS
clock = pygame.time.Clock()
FPS = 60

# Font
font = pygame.font.SysFont("arial", 36)
title_font = pygame.font.SysFont("arial", 72)

# Load background image
background_image = pygame.image.load("4107909.jpg").convert()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Spaceship class
class Spaceship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("spaceship_bg_removed.png.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 40))
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        self.speed = 5
        self.health = 10

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed  
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -7

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# Boss Bullet class
class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 7

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.image.load("enemy space impact.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))  
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# Boss class
class Boss(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        boss_images = [
            pygame.image.load("boss levels1.png").convert_alpha(),
            pygame.image.load("boss levels2.png").convert_alpha(),
            pygame.image.load("boss levels3.png").convert_alpha(),
        ]
        self.image = pygame.transform.scale(boss_images[level - 1], (120, 80))
        self.rect = self.image.get_rect(center=(WIDTH // 2, 100))
        self.speed = 3
        self.health = 10 * level

    def update(self):
        self.rect.x += self.speed
        if self.rect.right > WIDTH or self.rect.left < 0:
            self.speed *= -1

    def shoot(self):
        bullet = BossBullet(self.rect.centerx, self.rect.bottom)
        return bullet

# Initialize sprites
player = Spaceship()
player_group = pygame.sprite.Group(player)

bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
boss_group = pygame.sprite.Group()

# Main menu function
def main_menu():
    title_text = title_font.render("SPACE IMPACT", True, WHITE)
    start_text = font.render("Press ENTER to Start", True, WHITE)
    logo_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    show_start = True
    blink_timer = 0

    while True:
        screen.blit(background_image, (0, 0))
        screen.blit(title_text, logo_rect)
        if show_start:
            screen.blit(start_text, start_rect)

        pygame.display.flip()

        blink_timer += 1
        if blink_timer > FPS // 2:
            show_start = not show_start
            blink_timer = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

# Level selection screen
def level_selection():
    select_text = font.render("Select Level:", True, WHITE)
    levels = [1, 2, 3]
    selected_level = 0
    select_rect = select_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))

    while True:
        screen.blit(background_image, (0, 0))
        screen.blit(select_text, select_rect)

        for i, level in enumerate(levels):
            color = YELLOW if i == selected_level else WHITE
            level_text = font.render(f"Level {level}", True, color)
            level_rect = level_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 50))
            screen.blit(level_text, level_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_level = (selected_level - 1) % len(levels)
                if event.key == pygame.K_DOWN:
                    selected_level = (selected_level + 1) % len(levels)
                if event.key == pygame.K_RETURN:
                    return levels[selected_level]

# Main game loop
def play_level(selected_level):
    global running, player
    boss_fight = False
    player.health = 10
    boss_group.empty()
    enemies.empty()
    bullets.empty()

    boss = Boss(selected_level)
    enemy_kill_count = 0
    enemy_target = selected_level * 5

    last_hit_time = 0
    collision_cooldown = 500  # in milliseconds

    enemy_speed = [2, 4, 6][selected_level - 1]
    enemy_health = [1, 2, 3][selected_level - 1]

    while True:
        keys = pygame.key.get_pressed()
        screen.blit(background_image, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    bullets.add(bullet)

        if not boss_fight and len(enemies) < selected_level * 3:
            x = random.randint(0, WIDTH - 40)
            y = random.randint(-100, -40)
            speed = random.randint(2, enemy_speed)
            enemy = Enemy(x, y, speed)
            enemies.add(enemy)

        if enemy_kill_count >= enemy_target and not boss_fight:
            boss_group.add(boss)
            boss_fight = True

        player_group.update(keys)
        bullets.update()
        enemies.update()
        boss_group.update()

        current_time = pygame.time.get_ticks()

        if pygame.sprite.spritecollideany(player, enemies):
            if current_time - last_hit_time > collision_cooldown:
                player.health -= 1
                last_hit_time = current_time

        if pygame.sprite.spritecollideany(player, boss_group):
            if current_time - last_hit_time > collision_cooldown:
                player.health -= 1
                last_hit_time = current_time

        # Collision check for boss bullets
        for boss_bullet in pygame.sprite.spritecollide(player, bullets, False):
            if current_time - last_hit_time > collision_cooldown:
                player.health -= 1
                last_hit_time = current_time
                boss_bullet.kill()  # Remove the bullet after it hits the player

        if player.health <= 0:
            pygame.quit()
            sys.exit()

        for enemy in pygame.sprite.groupcollide(enemies, bullets, True, True):
            enemy_kill_count += 1

        for bullet in pygame.sprite.spritecollide(boss, bullets, True):
            boss.health -= 1
        if boss.health <= 0:
            return  # After defeating the boss, return to the level selection

        if boss_fight:
            # Boss shooting logic
            if random.randint(0, 100) < 2:  # 2% chance to shoot each frame
                boss_bullet = boss.shoot()
                bullets.add(boss_bullet)

        player_group.draw(screen)
        bullets.draw(screen)
        enemies.draw(screen)
        boss_group.draw(screen)

        level_text = font.render(f"Level: {selected_level}", True, WHITE)
        health_text = font.render(f"Health: {player.health}", True, WHITE)
        boss_health_text = font.render(f"Boss Health: {boss.health if boss_fight else '---'}", True, WHITE)
        screen.blit(level_text, (10, 10))
        screen.blit(health_text, (10, 40))
        screen.blit(boss_health_text, (WIDTH - 200, 10))

        pygame.display.flip()
        clock.tick(FPS)

# Start the game
def main():
    main_menu()
    while True:
        selected_level = level_selection()
        play_level(selected_level)  # Play the selected level
        # After defeating the boss, return to level selection

# Run the main game loop
if __name__ == "__main__":
    main()
