import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

class Player:
    def _init_(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 40
        self.speed = 5
        self.health = 100
        self.max_health = 100
        
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed
    
    def draw(self, screen):
        # Draw player ship as a triangle
        points = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, GREEN, points)
        
        # Draw health bar
        bar_width = 60
        bar_height = 8
        bar_x = self.x - 5
        bar_y = self.y - 15
        
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = int((self.health / self.max_health) * bar_width)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))

class Bullet:
    def __init__(self, x, y, direction=1):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 10
        self.speed = 7 * direction
        self.direction = direction
        
    def update(self):
        self.y -= self.speed
        
    def draw(self, screen):
        color = YELLOW if self.direction == 1 else RED
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        
    def is_off_screen(self):
        return self.y < 0 or self.y > SCREEN_HEIGHT

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.speed = random.uniform(1, 3)
        self.health = 30
        self.max_health = 30
        self.shoot_timer = 0
        self.shoot_delay = random.randint(60, 180)
        
    def update(self):
        self.y += self.speed
        self.shoot_timer += 1
        
    def draw(self, screen):
        # Draw enemy ship as an inverted triangle
        points = [
            (self.x + self.width // 2, self.y + self.height),
            (self.x, self.y),
            (self.x + self.width, self.y)
        ]
        pygame.draw.polygon(screen, RED, points)
        
    def can_shoot(self):
        if self.shoot_timer >= self.shoot_delay:
            self.shoot_timer = 0
            self.shoot_delay = random.randint(60, 180)
            return True
        return False
        
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

class Powerup:
    def __init__(self, x, y, type_name):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.speed = 2
        self.type = type_name  # 'health' or 'rapid_fire'
        
    def update(self):
        self.y += self.speed
        
    def draw(self, screen):
        color = GREEN if self.type == 'health' else BLUE
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        # Draw + for health, R for rapid fire
        if self.type == 'health':
            pygame.draw.line(screen, WHITE, (self.x + 10, self.y + 5), (self.x + 10, self.y + 15), 2)
            pygame.draw.line(screen, WHITE, (self.x + 5, self.y + 10), (self.x + 15, self.y + 10), 2)
        else:
            font = pygame.font.Font(None, 16)
            text = font.render('R', True, WHITE)
            screen.blit(text, (self.x + 6, self.y + 2))
        
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Shooter")
        self.clock = pygame.time.Clock()
        
        self.player = Player(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 60)
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.powerups = []
        
        self.score = 0
        self.level = 1
        self.enemy_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.rapid_fire_timer = 0
        
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.running = True
        self.game_over = False
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    # Shoot bullet
                    bullet_x = self.player.x + self.player.width // 2 - 2
                    bullet_y = self.player.y
                    self.bullets.append(Bullet(bullet_x, bullet_y))
                elif event.key == pygame.K_r and self.game_over:
                    self.restart_game()
                    
    def restart_game(self):
        self.player = Player(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 60)
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.powerups = []
        self.score = 0
        self.level = 1
        self.enemy_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.rapid_fire_timer = 0
        self.game_over = False
        
    def spawn_enemies(self):
        self.enemy_spawn_timer += 1
        spawn_rate = max(30 - self.level * 2, 10)
        
        if self.enemy_spawn_timer >= spawn_rate:
            self.enemy_spawn_timer = 0
            x = random.randint(0, SCREEN_WIDTH - 40)
            self.enemies.append(Enemy(x, -30))
            
    def spawn_powerups(self):
        self.powerup_spawn_timer += 1
        if self.powerup_spawn_timer >= 600:  # Every 10 seconds
            self.powerup_spawn_timer = 0
            x = random.randint(0, SCREEN_WIDTH - 20)
            powerup_type = random.choice(['health', 'rapid_fire'])
            self.powerups.append(Powerup(x, -20, powerup_type))
            
    def update(self):
        if self.game_over:
            return
            
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        
        # Rapid fire shooting
        if keys[pygame.K_SPACE] and self.rapid_fire_timer > 0:
            if len(self.bullets) == 0 or self.bullets[-1].y < self.player.y - 20:
                bullet_x = self.player.x + self.player.width // 2 - 2
                bullet_y = self.player.y
                self.bullets.append(Bullet(bullet_x, bullet_y))
        
        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= 1
        
        # Spawn enemies and powerups
        self.spawn_enemies()
        self.spawn_powerups()
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
                
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.enemy_bullets.remove(bullet)
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.is_off_screen():
                self.enemies.remove(enemy)
            elif enemy.can_shoot():
                bullet_x = enemy.x + enemy.width // 2 - 2
                bullet_y = enemy.y + enemy.height
                self.enemy_bullets.append(Bullet(bullet_x, bullet_y, -1))
        
        # Update powerups
        for powerup in self.powerups[:]:
            powerup.update()
            if powerup.is_off_screen():
                self.powerups.remove(powerup)
        
        # Check collisions
        self.check_collisions()
        
        # Update level
        if self.score > 0 and self.score % 500 == 0:
            self.level = (self.score // 500) + 1
            
    def check_collisions(self):
        # Player bullets vs enemies
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if (bullet.x < enemy.x + enemy.width and
                    bullet.x + bullet.width > enemy.x and
                    bullet.y < enemy.y + enemy.height and
                    bullet.y + bullet.height > enemy.y):
                    
                    self.bullets.remove(bullet)
                    enemy.health -= 20
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.score += 100
                    break
        
        # Enemy bullets vs player
        for bullet in self.enemy_bullets[:]:
            if (bullet.x < self.player.x + self.player.width and
                bullet.x + bullet.width > self.player.x and
                bullet.y < self.player.y + self.player.height and
                bullet.y + bullet.height > self.player.y):
                
                self.enemy_bullets.remove(bullet)
                self.player.health -= 20
                if self.player.health <= 0:
                    self.game_over = True
        
        # Enemies vs player
        for enemy in self.enemies[:]:
            if (enemy.x < self.player.x + self.player.width and
                enemy.x + enemy.width > self.player.x and
                enemy.y < self.player.y + self.player.height and
                enemy.y + enemy.height > self.player.y):
                
                self.enemies.remove(enemy)
                self.player.health -= 30
                if self.player.health <= 0:
                    self.game_over = True
        
        # Powerups vs player
        for powerup in self.powerups[:]:
            if (powerup.x < self.player.x + self.player.width and
                powerup.x + powerup.width > self.player.x and
                powerup.y < self.player.y + self.player.height and
                powerup.y + powerup.height > self.player.y):
                
                self.powerups.remove(powerup)
                if powerup.type == 'health':
                    self.player.health = min(self.player.max_health, self.player.health + 30)
                elif powerup.type == 'rapid_fire':
                    self.rapid_fire_timer = 300  # 5 seconds at 60 FPS
                    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw stars background
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(self.screen, WHITE, (x, y), 1)
        
        if not self.game_over:
            # Draw game objects
            self.player.draw(self.screen)
            
            for bullet in self.bullets:
                bullet.draw(self.screen)
                
            for bullet in self.enemy_bullets:
                bullet.draw(self.screen)
                
            for enemy in self.enemies:
                enemy.draw(self.screen)
                
            for powerup in self.powerups:
                powerup.draw(self.screen)
            
            # Draw UI
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            level_text = self.font.render(f"Level: {self.level}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(level_text, (10, 50))
            
            if self.rapid_fire_timer > 0:
                rapid_text = self.small_font.render("RAPID FIRE!", True, YELLOW)
                self.screen.blit(rapid_text, (SCREEN_WIDTH - 120, 10))
        else:
            # Game over screen
            game_over_text = self.font.render("GAME OVER", True, RED)
            final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.small_font.render("Press R to restart", True, WHITE)
            
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 20))
        
        pygame.display.flip()
        
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()