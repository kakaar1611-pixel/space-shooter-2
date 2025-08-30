import pygame
import random
import sys
import math

pygame.init()

# Konstanta
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SPEED = 5
BULLET_SPEED = 7
ENEMY_SPEED_MIN = 1
ENEMY_SPEED_MAX = 3
INITIAL_ENEMY_SPAWN_RATE = 60  # frames
MIN_ENEMY_SPAWN_RATE = 20  # Batas minimum spawn rate

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Buat layar
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter 2")
clock = pygame.time.Clock()

# Font
font = pygame.font.SysFont('Arial', 32)
big_font = pygame.font.SysFont('Arial', 64)

# Buat background bintang yang tetap
stars = []
for _ in range(100):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    size = random.randint(1, 3)
    stars.append((x, y, size))

class Player:
    def __init__(self):
        self.width = 50
        self.height = 30
        self.rect = pygame.Rect(SCREEN_WIDTH // 2 - self.width // 2, 
                               SCREEN_HEIGHT - self.height - 20, 
                               self.width, self.height)
        self.speed = PLAYER_SPEED
        self.bullets = []
        self.shoot_cooldown = 0
        
    def update(self):
        keys = pygame.key.get_pressed()
        
        # Gerakan horizontal
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
            
        # Tembak peluru
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        if keys[pygame.K_SPACE] and self.shoot_cooldown == 0:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            self.bullets.append(bullet)
            self.shoot_cooldown = 15  # Cooldown tembakan
            
        # Update peluru
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.rect.bottom < 0:
                self.bullets.remove(bullet)
                
    def draw(self, surface):
        # Gambar pesawat (segitiga)
        points = [
            (self.rect.centerx, self.rect.top),
            (self.rect.left, self.rect.bottom),
            (self.rect.right, self.rect.bottom)
        ]
        pygame.draw.polygon(surface, BLUE, points)
        pygame.draw.polygon(surface, WHITE, points, 2)
        
        # Gambar peluru
        for bullet in self.bullets:
            bullet.draw(surface)
            
    def get_hit(self):
        # Efek terkena tembakan
        pass

class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 2, y, 4, 10)
        self.speed = BULLET_SPEED
        
    def update(self):
        self.rect.y -= self.speed
        
    def draw(self, surface):
        pygame.draw.rect(surface, YELLOW, self.rect)

class Enemy:
    def __init__(self):
        self.size = random.randint(20, 40)
        self.rect = pygame.Rect(random.randint(0, SCREEN_WIDTH - self.size), 
                               -self.size, 
                               self.size, self.size)
        self.speed = random.uniform(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
        self.color = random.choice([RED, GREEN, PURPLE])
        self.points = 50 - self.size  # Semakin kecil musuh, semakin besar poin
        
    def update(self):
        self.rect.y += self.speed
        
    def draw(self, surface):
        # Gambar musuh (bentuk diamond)
        points = [
            (self.rect.centerx, self.rect.top),
            (self.rect.right, self.rect.centery),
            (self.rect.centerx, self.rect.bottom),
            (self.rect.left, self.rect.centery)
        ]
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, WHITE, points, 2)

class Explosion:
    def __init__(self, x, y, size=30):
        self.x = x
        self.y = y
        self.size = size
        self.max_size = size * 2
        self.growth_rate = 2
        self.alpha = 255
        self.frame = 0
        
    def update(self):
        self.frame += 1
        self.size += self.growth_rate
        self.alpha -= 15
        return self.alpha > 0
        
    def draw(self, surface):
        # Buat permukaan transparan untuk efek ledakan
        explosion_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        # Gambar lingkaran dengan alpha berkurang
        for i in range(3):
            radius = max(5, self.size - i * 5)
            alpha = max(0, self.alpha - i * 50)
            if i == 0:
                color = (*YELLOW[:3], alpha)
            else:
                color = (*RED[:3], alpha)
            pygame.draw.circle(explosion_surf, color, (self.size, self.size), radius)
            
        surface.blit(explosion_surf, (self.x - self.size, self.y - self.size))

def show_game_over(score):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    game_over_text = big_font.render("GAME OVER", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    restart_text = font.render("Press SPACE to restart or ESC to quit", True, WHITE)
    
    screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 100))
    screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))
    screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 60))
    
    pygame.display.flip()

def main():
    player = Player()
    enemies = []
    explosions = []
    score = 0
    lives = 3
    enemy_spawn_timer = 0
    enemy_spawn_rate = INITIAL_ENEMY_SPAWN_RATE  # Gunakan variabel lokal untuk spawn rate
    game_over = False
    
    running = True
    while running:
        clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over and event.key == pygame.K_SPACE:
                    # Reset game
                    player = Player()
                    enemies = []
                    explosions = []
                    score = 0
                    lives = 3
                    enemy_spawn_timer = 0
                    enemy_spawn_rate = INITIAL_ENEMY_SPAWN_RATE  # Reset spawn rate
                    game_over = False
        
        if not game_over:
            # Update player
            player.update()
            
            # Spawn musuh
            enemy_spawn_timer += 1
            if enemy_spawn_timer >= enemy_spawn_rate:
                enemies.append(Enemy())
                enemy_spawn_timer = 0
                
                # Tingkatkan kesulitan seiring waktu
                if enemy_spawn_rate > MIN_ENEMY_SPAWN_RATE:
                    enemy_spawn_rate -= 0.1
                    
            # Update musuh dan cek tabrakan
            for enemy in enemies[:]:
                enemy.update()
                
                # Cek tabrakan dengan peluru
                hit_by_bullet = False
                for bullet in player.bullets[:]:
                    if enemy.rect.colliderect(bullet.rect):
                        enemies.remove(enemy)
                        player.bullets.remove(bullet)
                        score += enemy.points
                        explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery, enemy.size))
                        hit_by_bullet = True
                        break
                
                # Jika musuh sudah terkena peluru, lanjut ke musuh berikutnya
                if hit_by_bullet:
                    continue
                
                # Cek tabrakan dengan pemain
                if enemy.rect.colliderect(player.rect):
                    enemies.remove(enemy)
                    lives -= 1
                    explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery, enemy.size))
                    if lives <= 0:
                        game_over = True
                
                # Cek musuh lewat layar
                elif enemy.rect.top > SCREEN_HEIGHT:
                    enemies.remove(enemy)
                    lives -= 1
                    if lives <= 0:
                        game_over = True
            
            # Update ledakan
            for explosion in explosions[:]:
                if not explosion.update():
                    explosions.remove(explosion)
            
            # Clear screen
            screen.fill(BLACK)
            
            # Gambar bintang latar belakang (tetap)
            for x, y, size in stars:
                pygame.draw.circle(screen, WHITE, (x, y), size)
            
            # Draw player
            player.draw(screen)
            
            # Draw enemies
            for enemy in enemies:
                enemy.draw(screen)
                
            # Draw explosions
            for explosion in explosions:
                explosion.draw(screen)
            
            # Draw UI
            score_text = font.render(f"Score: {score}", True, WHITE)
            lives_text = font.render(f"Lives: {lives}", True, WHITE)
            screen.blit(score_text, (10, 10))
            screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 10, 10))
            
        else:
            show_game_over(score)
        
        # Update display
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
