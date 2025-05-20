import pygame
import sys

# === Инициализация ===
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Аркада — Главное меню, Победа и Поражение")
clock = pygame.time.Clock()
FPS = 60

# === Цвета ===
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY = (200, 200, 255)
GREEN = (0, 200, 100)
BLUE = (0, 128, 255)
YELLOW = (255, 255, 0)
RED = (200, 0, 0)
MAGENTA = (255, 0, 255)
GRAY = (100, 100, 100)

# === Игрок ===
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.color = BLUE
        self.speed = 5
        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_strength = 10
        self.on_ground = False

    def update(self, keys, platforms):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = -self.jump_strength

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.velocity_y > 0:
                    self.rect.bottom = plat.top
                    self.velocity_y = 0
                    self.on_ground = True

    def draw(self, surface, camera_scroll):
        pygame.draw.rect(surface, self.color,
                         (self.rect.x - camera_scroll, self.rect.y, self.rect.width, self.rect.height))

# === Враг ===
class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.speed = 2

    def update(self):
        self.rect.x += self.speed
        if self.rect.left < 0 or self.rect.right > 2000:
            self.speed *= -1

    def draw(self, surface, camera_scroll):
        pygame.draw.rect(surface, RED,
                         (self.rect.x - camera_scroll, self.rect.y, self.rect.width, self.rect.height))

# === Уровень ===
class Level:
    def __init__(self, num):
        self.platforms = [pygame.Rect(i * 250, 500, 150, 20) for i in range(10)]
        self.portal = pygame.Rect(1800, 460, 40, 40) if num == 1 else None
        self.return_portal = pygame.Rect(50, 460, 40, 40) if num == 2 else None
        self.artifact = pygame.Rect(1950, 450, 30, 30) if num == 2 else None
        self.finish_door = pygame.Rect(2000, 460, 40, 40) if num == 1 else None
        self.enemies = [Enemy(500, 460), Enemy(900, 460)] if num == 1 else []

    def update(self):
        for e in self.enemies:
            e.update()

    def draw(self, surface, camera_scroll):
        surface.fill(SKY)
        for plat in self.platforms:
            pygame.draw.rect(surface, GREEN,
                             pygame.Rect(plat.x - camera_scroll, plat.y, plat.width, plat.height))
        if self.portal:
            pygame.draw.rect(surface, YELLOW,
                             pygame.Rect(self.portal.x - camera_scroll, self.portal.y,
                                         self.portal.width, self.portal.height))
        if self.return_portal:
            pygame.draw.rect(surface, YELLOW,
                             pygame.Rect(self.return_portal.x - camera_scroll, self.return_portal.y,
                                         self.return_portal.width, self.return_portal.height))
        if self.artifact:
            pygame.draw.rect(surface, MAGENTA,
                             pygame.Rect(self.artifact.x - camera_scroll, self.artifact.y,
                                         self.artifact.width, self.artifact.height))
        if self.finish_door:
            pygame.draw.rect(surface, GRAY,
                             pygame.Rect(self.finish_door.x - camera_scroll, self.finish_door.y,
                                         self.finish_door.width, self.finish_door.height))
        for e in self.enemies:
            e.draw(surface, camera_scroll)

# === Игра ===
class Game:
    def __init__(self):
        self.menu_options = ["Начать игру", "Выход"]
        self.menu_selected = 0
        self.state = "main_menu"
        self.reset_all()

    def reset_all(self):
        self.player = Player(100, 400)
        self.level = Level(1)
        self.camera_scroll = 0
        self.current_level = 1
        self.lives = 3
        self.score = 0
        self.win = False

    def run(self):
        while True:
            keys = pygame.key.get_pressed()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.state == "main_menu":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self.menu_selected = (self.menu_selected - 1) % len(self.menu_options)
                        elif event.key == pygame.K_DOWN:
                            self.menu_selected = (self.menu_selected + 1) % len(self.menu_options)
                        elif event.key == pygame.K_RETURN:
                            if self.menu_selected == 0:
                                self.state = "playing"
                            elif self.menu_selected == 1:
                                pygame.quit()
                                sys.exit()

                elif self.state in ["game_over", "win"]:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.state = "main_menu"
                        self.reset_all()

            if self.state == "playing":
                self.player.update(keys, self.level.platforms)
                self.level.update()
                self.check_collisions()
                self.update_camera()

            self.draw()
            pygame.display.flip()
            clock.tick(FPS)

    def update_camera(self):
        left_border = SCREEN_WIDTH // 4
        right_border = SCREEN_WIDTH * 3 // 4
        px = self.player.rect.x
        if px - self.camera_scroll < left_border:
            self.camera_scroll = max(0, px - left_border)
        elif px - self.camera_scroll > right_border:
            self.camera_scroll = px - right_border

    def check_collisions(self):
        if self.level.portal and self.player.rect.colliderect(self.level.portal):
            self.current_level = 2
            self.level = Level(2)
            portal_x = self.level.return_portal.right if self.level.return_portal else 100
            self.player.rect.topleft = (portal_x + 10, self.level.return_portal.y - self.player.rect.height)

        if self.level.return_portal and self.player.rect.colliderect(self.level.return_portal):
            self.current_level = 1
            self.level = Level(1)
            self.player.rect.topleft = (1800, 400)

        if self.level.artifact and self.player.rect.colliderect(self.level.artifact):
            self.lives += 1
            self.level.artifact = None

        if self.level.finish_door and self.player.rect.colliderect(self.level.finish_door):
            self.state = "win"

        for enemy in self.level.enemies[:]:
            if self.player.rect.colliderect(enemy.rect):
                if self.player.velocity_y > 0:
                    self.level.enemies.remove(enemy)
                    self.score += 100
                    self.player.velocity_y = -10
                else:
                    self.lose_life()

        if self.player.rect.y > SCREEN_HEIGHT:
            self.lose_life()

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.state = "game_over"
        else:
            self.player.rect.topleft = (100, 400)
            self.player.velocity_y = 0
            self.camera_scroll = 0

    def draw(self):
        if self.state == "main_menu":
            self.draw_menu()
            return

        self.level.draw(screen, self.camera_scroll)
        self.player.draw(screen, self.camera_scroll)

        font = pygame.font.SysFont("Arial", 24)
        screen.blit(font.render(f"Жизни: {self.lives}", True, BLACK), (10, 10))
        screen.blit(font.render(f"Очки: {self.score}", True, BLACK), (10, 40))

        if self.state == "win":
            self.show_message("YOU WIN! Нажмите Enter", SKY)
        if self.state == "game_over":
            self.show_message("YOU LOSE! Нажмите Enter", RED)

    def draw_menu(self):
        screen.fill(BLACK)
        font = pygame.font.SysFont("Arial", 36)
        for i, option in enumerate(self.menu_options):
            color = YELLOW if i == self.menu_selected else WHITE
            text = font.render(option, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, 250 + i * 50))
            screen.blit(text, rect)

    def show_message(self, text, color):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(color)
        screen.blit(overlay, (0, 0))
        font = pygame.font.SysFont("Arial", 48)
        text_surface = font.render(text, True, BLACK)
        rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text_surface, rect)

# === Запуск ===
Game().run()
