# python shooting game samaple
import pygame
import random
import sys

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (255, 255, 0)

# 画面設定
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

PLAYER_WIDTH = 60
PLAYER_HEIGHT = 30

BULLET_WIDTH = 5
BULLET_HEIGHT = 10

ENEMY_WIDTH = 30
ENEMY_HEIGHT = 30

# ゲーム設定
FPS = 60

# プレイヤークラス
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.speed = 10

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed
     
# 弾丸クラス
class Bullet(pygame.sprite.Sprite)  :
    def __init__(self, x, y):
        super().__init__()    
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 14

    def update(self):
        self.rect.y -= self.speed
        if self.rect.top < 0:
            self.kill()
# 敵クラス
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(30, SCREEN_WIDTH - 30), random.randint(-100, -30))
        self.speed = random.randint(2, 9)
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill() 

# メインゲームループ
def main():
    # 初期化
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("サンプルシューティングゲーム")
    clock = pygame.time.Clock()
    
    player = pygame.sprite.GroupSingle(Player())

    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    score = 0
    font = pygame.font.SysFont('applemyungjo', 14)
    
    # 敵の出現タイマー
    enemy_timer = 0
    enemy_spawn_rate = 60  # 60フレームごとに敵出現
    
    running = True
    
    while running:
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # 弾を発射
                    bullet = Bullet(player.sprite.rect.centerx - BULLET_WIDTH // 2, player.sprite.rect.top)
                    bullets.add(bullet)
                    bullet = Bullet(player.sprite.rect.centerx + player.sprite.rect.width // 2 - BULLET_WIDTH // 2, player.sprite.rect.top)
                    bullets.add(bullet)
        bullets.update()

        player.update()

        # 敵の出現
        enemy_timer += 1
        if enemy_timer >= enemy_spawn_rate:
            enemies.add(Enemy())
            enemy_timer = 0

        enemies.update()
        
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        score += len(hits) * 10
        
        # プレイヤーと敵の当たり判定（ゲームオーバー）
        if pygame.sprite.spritecollide(player.sprite, enemies, False):
            print(f"Game Over! Final Score: {score}")
            running = False 

        screen.fill(BLACK)
        
        # オブジェクト描画
        player.draw(screen)
        bullets.draw(screen)
        enemies.draw(screen)
        
        # スコア表示
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # 操作説明
        help_text = font.render("Arrow keys: Move, Space: Shoot", True, WHITE)
        screen.blit(help_text, (10, SCREEN_HEIGHT - 40))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

# メイン関数実行
if __name__ == "__main__":
    main()