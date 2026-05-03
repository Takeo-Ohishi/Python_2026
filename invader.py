import pygame
import sys
import random
import os

# 画面設定
WIDTH, HEIGHT = 800, 600

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

ENEMY_WIDTH = 40
ENEMY_HEIGHT = 35
ENEMY_SPEED = 10

PLAYER_SPEED = 5

BULLET_WIDTH = 5
BULLET_HEIGHT = 10
BULLET_SPEED = 10

ENEMY_BULLET_RADIUS = 5
TOCHKA_SIZE = 10

# 画像ファイル
BASE_DIR = os.path.dirname(__file__)
IMG_PATH = os.path.join(BASE_DIR, "space-invaders/")
ENEMY_IMGs = ["enemy1_1.png", "enemy2_1.png", "enemy2_2.png", "enemy3_1.png", "enemy3_2.png"]
PLAYER_IMG = "ship.png"

class Enemy(pygame.sprite.Sprite):
    def __init__(self, row, col):
        super().__init__()
        self.image = pygame.image.load(IMG_PATH + ENEMY_IMGs[row]).convert_alpha()
        self.image = pygame.transform.scale(self.image, (ENEMY_WIDTH, ENEMY_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.topleft = (col * (ENEMY_WIDTH + 10) + 150, row * (ENEMY_HEIGHT + 10) + 55)
        self.enemy_clock = 0
        self.sv_direction = -1
        self.enemy_bullet_clock = random.randint(0, 60)  # 弾を撃つタイミングをランダムに設定

    def update(self, direction):
        self.enemy_clock += 1
        self.enemy_bullet_clock += 1
        if self.enemy_clock >= 60:  # 1秒ごとに移動
            self.enemy_clock = 0  # クロックをリセット
            if self.sv_direction != direction:
                self.sv_direction = direction
                self.rect.y += 55  # 敵を下に移動
            else:
                self.rect.x += ENEMY_SPEED * direction

class Enemy_Bullet(pygame.sprite.Sprite)  :
    def __init__(self, x, y):
        super().__init__()    
        self.image = pygame.Surface((ENEMY_BULLET_RADIUS * 2, ENEMY_BULLET_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (ENEMY_BULLET_RADIUS, ENEMY_BULLET_RADIUS), ENEMY_BULLET_RADIUS)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 1.5 * ENEMY_SPEED

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(IMG_PATH + PLAYER_IMG).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 35)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += PLAYER_SPEED

class Bullet(pygame.sprite.Sprite)  :
    def __init__(self, x, y):
        super().__init__()    
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.y -= BULLET_SPEED
        if self.rect.top < 0:
            self.kill()

class Tochka(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()    
        self.image = pygame.Surface((TOCHKA_SIZE, TOCHKA_SIZE))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    def update(self):
        pass

def main():
    # Pygameの初期化
    pygame.init()  
    # 画面の設定
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    # タイトルバーの設定（表示する文字を指定）
    pygame.display.set_caption("スペースインベーダー") 
    clock = pygame.time.Clock()
    
    # 敵のグループを作成
    enemies = pygame.sprite.Group()
    for row in range(5):
        for col in range(10):
            enemy = Enemy(row, col)
            enemies.add(enemy)

    player = pygame.sprite.GroupSingle(Player())
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()

    # トーチカのグループを作成
    tochkas = pygame.sprite.Group()  # 衝突点を表示するためのグループ 
    for number in range(4):
        for row in range(4):
            for col in range(10):
                tochka = Tochka(50 + 200 * number + TOCHKA_SIZE * col , 450 + TOCHKA_SIZE * row )
                tochkas.add(tochka)

    running = True
    direction = -1  # 1:右, -1:左
    score = 0
    damege = 0
    font = pygame.font.SysFont(None, 48)

    while running:
        # 画面を黒色(#000000)に塗りつぶし
        screen.fill((0, 0, 0))
        clock.tick(60)  
    
        # イベント処理
        for event in pygame.event.get():
            # 閉じるボタンが押されたら終了
            if event.type == pygame.QUIT:  
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # 弾を発射
                    bullet = Bullet(player.sprite.rect.centerx, player.sprite.rect.top)
                    bullets.add(bullet)

        is_clear = True
        for enemy in enemies:
            is_clear = False
            if random.random() < 0.01:  # 1%の確率で弾を撃つ敵
                enemy_bullet = Enemy_Bullet(enemy.rect.centerx, enemy.rect.bottom)
                enemy_bullets.add(enemy_bullet) 
            if enemy.rect.right >= WIDTH - 30:
                direction = -1
                break
            if enemy.rect.left <= 30:
                direction = 1
                break
            if enemy.rect.bottom >= HEIGHT - 30:
                running = False
                break

        if is_clear:
            running = False

        # 敵の更新と描画
        enemies.update(direction)
        enemies.draw(screen)
        player.update()
        player.draw(screen)
        bullets.update()
        bullets.draw(screen)
        enemy_bullets.update()
        enemy_bullets.draw(screen)
        tochkas.update()
        tochkas.draw(screen)

        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        score += len(hits) * 10
        hits = pygame.sprite.spritecollide(player.sprite, enemy_bullets, True)
        damege += len(hits) * 10
        if damege > 100:
             running = False
        pygame.sprite.groupcollide(enemy_bullets, bullets, True, True)
        pygame.sprite.groupcollide(tochkas, bullets, True, True)
        pygame.sprite.groupcollide(tochkas, enemy_bullets, True, True)

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        damage_text = font.render(f"Damage: {damege}", True, WHITE)
        screen.blit(damage_text, (WIDTH - damage_text.get_width() - 10, 10))
        
        # 画面の更新
        pygame.display.flip()  

    # ゲーム終了後の待機ループ
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
        game_over_text = font.render("GAME OVER", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
        pygame.display.flip()
        clock.tick(60)  
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()