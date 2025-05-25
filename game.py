import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zombie Survival")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Clock for controlling game speed
clock = pygame.time.Clock()
FPS = 60

# Load images
def load_image(name, scale=1):
    try:
        image = pygame.image.load(name).convert_alpha()
        width = image.get_width()
        height = image.get_height()
        image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        return image
    except pygame.error:
        # If image loading fails, create a colored rectangle as placeholder
        surf = pygame.Surface((30, 30))
        surf.fill(RED if "zombie" in name else BLUE if "player" in name else GREEN)
        return surf

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("C:\Users\ibrahim laptops\Downloads\e.png", 0.1)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.ammo = 30
        self.max_ammo = 50
        self.score = 0
        self.last_shot = pygame.time.get_ticks()
        self.shoot_cooldown = 300  # milliseconds

    def update(self):
        # Get key presses
        keys = pygame.key.get_pressed()

        # Movement
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_s] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_cooldown and self.ammo > 0:
            self.last_shot = now
            self.ammo -= 1
            return True
        return False

    def draw_health_bar(self, surface):
        # Health bar
        pygame.draw.rect(surface, RED, (10, 10, 200, 20))
        pygame.draw.rect(surface, GREEN, (10, 10, 200 * (self.health / self.max_health), 20))

    def draw_ammo_bar(self, surface):
        # Ammo bar
        pygame.draw.rect(surface, BLACK, (10, 40, 200, 20))
        pygame.draw.rect(surface, BLUE, (10, 40, 200 * (self.ammo / self.max_ammo), 20))

# Zombie class
class Zombie(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("C:\Users\ibrahim laptops\Downloads\d4f48b8315485a3753cd3a7181f59d20.png", 0.1)
        self.rect = self.image.get_rect()

        # Spawn zombies outside the screen
        side = random.randint(0, 3)
        if side == 0:  # Top
            self.rect.x = random.randint(0, SCREEN_WIDTH)
            self.rect.y = -50
        elif side == 1:  # Right
            self.rect.x = SCREEN_WIDTH + 50
            self.rect.y = random.randint(0, SCREEN_HEIGHT)
        elif side == 2:  # Bottom
            self.rect.x = random.randint(0, SCREEN_WIDTH)
            self.rect.y = SCREEN_HEIGHT + 50
        else:  # Left
            self.rect.x = -50
            self.rect.y = random.randint(0, SCREEN_HEIGHT)

        self.speed = random.uniform(1.0, 2.5)
        self.health = 100

    def update(self, player):
        # Move towards player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)

        if dist != 0:
            dx = dx / dist
            dy = dy / dist

        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

        # Check collision with player
        if self.rect.colliderect(player.rect):
            player.health -= 0.5  # Damage player on contact

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, mouse_x, mouse_y):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        # Calculate direction
        dx = mouse_x - x
        dy = mouse_y - y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist != 0:
            dx = dx / dist
            dy = dy / dist

        self.speed = 10
        self.dx = dx * self.speed
        self.dy = dy * self.speed
        self.lifetime = 60  # frames

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.lifetime -= 1

        # Remove if out of screen or lifetime expired
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or
            self.lifetime <= 0):
            self.kill()

# Pickup class (health kit or ammo)
class Pickup(pygame.sprite.Sprite):
    def __init__(self, pickup_type):
        super().__init__()
        self.pickup_type = pickup_type  # "health" or "ammo"

        if pickup_type == "health":
            self.image = pygame.Surface((20, 20))
            self.image.fill(GREEN)
        else:  # ammo
            self.image = pygame.Surface((20, 20))
            self.image.fill(BLUE)

        self.rect = self.image.get_rect()
        self.rect.x = random.randint(50, SCREEN_WIDTH - 50)
        self.rect.y = random.randint(50, SCREEN_HEIGHT - 50)
        self.lifetime = 600  # 10 seconds at 60 FPS

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

# Game class
class Game:
    def __init__(self):
        self.player = Player()
        self.all_sprites = pygame.sprite.Group()
        self.zombies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.pickups = pygame.sprite.Group()

        self.all_sprites.add(self.player)

        self.font = pygame.font.SysFont(None, 36)
        self.zombie_spawn_timer = 0
        self.pickup_spawn_timer = 0
        self.game_over = False

    def spawn_zombie(self):
        zombie = Zombie()
        self.zombies.add(zombie)
        self.all_sprites.add(zombie)

    def spawn_pickup(self):
        pickup_type = random.choice(["health", "ammo"])
        pickup = Pickup(pickup_type)
        self.pickups.add(pickup)
        self.all_sprites.add(pickup)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                if event.button == 1:  # Left mouse button
                    if self.player.shoot():
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        bullet = Bullet(self.player.rect.centerx, self.player.rect.centery, mouse_x, mouse_y)
                        self.bullets.add(bullet)
                        self.all_sprites.add(bullet)

        return True

    def update(self):
        if not self.game_over:
            # Update all sprites
            self.player.update()
            self.zombies.update(self.player)
            self.bullets.update()
            self.pickups.update()

            # Check for bullet hits on zombies
            hits = pygame.sprite.groupcollide(self.zombies, self.bullets, False, True)
            for zombie, bullets_hit in hits.items():
                zombie.health -= 25 * len(bullets_hit)
                if zombie.health <= 0:
                    zombie.kill()
                    self.player.score += 10

            # Check for player pickup collisions
            hits = pygame.sprite.spritecollide(self.player, self.pickups, True)
            for pickup in hits:
                if pickup.pickup_type == "health":
                    self.player.health = min(self.player.health + 25, self.player.max_health)
                else:  # ammo
                    self.player.ammo = min(self.player.ammo + 15, self.player.max_ammo)

            # Spawn zombies
            self.zombie_spawn_timer += 1
            if self.zombie_spawn_timer >= 60:  # Every second at 60 FPS
                self.spawn_zombie()
                self.zombie_spawn_timer = 0

            # Spawn pickups
            self.pickup_spawn_timer += 1
            if self.pickup_spawn_timer >= 600:  # Every 10 seconds
                self.spawn_pickup()
                self.pickup_spawn_timer = 0

            # Check player health
            if self.player.health <= 0:
                self.game_over = True

    def draw(self):
        screen.fill(BLACK)

        self.all_sprites.draw(screen)

        # Draw HUD
        self.player.draw_health_bar(screen)
        self.player.draw_ammo_bar(screen)

        # Draw score
        score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH - 150, 10))

        # Game over message
        if self.game_over:
            game_over_text = self.font.render("GAME OVER! Press ESC to quit.", True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2))

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()
