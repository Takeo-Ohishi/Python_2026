import pygame
import sys
import random

# --- 定数 ---
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

# 色
WHITE = (255, 255, 255)
SKY_BLUE = (135, 206, 235)
GROUND_COLOR = (222, 216, 149)
PIPE_COLOR = (115, 191, 46)

# パラメータ
GRAVITY = 0.5
JUMP_STRENGTH = -8
PIPE_SPEED = 3
PIPE_WIDTH = 60
PIPE_GAP = 150
BIRD_SIZE = (40, 35) # 画像の縮小サイズ

# --- クラス ---
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.velocity = 0
        # 画像の読み込みとスケーリング
        img_a = pygame.image.load("Parrot-a.png").convert_alpha()
        img_b = pygame.image.load("Parrot-b.png").convert_alpha()
        self.frames = [
            pygame.transform.scale(img_a, BIRD_SIZE),
            pygame.transform.scale(img_b, BIRD_SIZE)
        ]
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        # 厳密な座標を保持するため
        self.y = y
        self.animation_timer = 0
        self.animation_speed = 10

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def update(self):
        # 重力
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.centery = self.y

        # アニメーション
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.animation_timer = 0

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, is_top=False):
        super().__init__()
        original_img = pygame.image.load('pipe.png').convert_alpha()
        # 土管の画像をパイプの幅と画面の高さに合わせてリサイズ
        img = pygame.transform.scale(original_img, (PIPE_WIDTH, SCREEN_HEIGHT))
        
        self.is_top = is_top
        self.passed = False

        if self.is_top:
            # 上の土管の場合は上下反転させる
            self.image = pygame.transform.flip(img, False, True)
            self.rect = self.image.get_rect()
            self.rect.bottomleft = (x, y)
        else:
            self.image = img
            self.rect = self.image.get_rect()
            self.rect.topleft = (x, y)

    def update(self):
        self.rect.x -= PIPE_SPEED
        if self.rect.right < 0:
            self.kill()

# --- 関数 ---
def spawn_pipes(x, group):
    gap_y = random.randint(50, SCREEN_HEIGHT - 50 - 100 - PIPE_GAP)
    top_pipe = Pipe(x, gap_y, is_top=True)
    bottom_pipe = Pipe(x, gap_y + PIPE_GAP, is_top=False)
    group.add(top_pipe, bottom_pipe)

# --- メイン処理 ---
def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Parrot")
    se1 = pygame.mixer.Sound("Bird.wav")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)

    # スプライトグループ
    all_sprites = pygame.sprite.Group()
    pipes_group = pygame.sprite.Group()

    # 鳥の生成
    bird = Bird(100, SCREEN_HEIGHT // 2)
    all_sprites.add(bird)

    # 最初の土管生成
    spawn_pipes(SCREEN_WIDTH + 100, pipes_group)
    all_sprites.add(pipes_group.sprites())

    score = 0
    game_over = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if game_over:
                        # リスタート
                        all_sprites.empty()
                        pipes_group.empty()
                        
                        bird = Bird(100, SCREEN_HEIGHT // 2)
                        all_sprites.add(bird)
                        spawn_pipes(SCREEN_WIDTH + 100, pipes_group)
                        all_sprites.add(pipes_group.sprites())
                        
                        score = 0
                        game_over = False
                    else:
                        bird.jump()
                        se1.play()  # 鳥のジャンプ音を再生
        if not game_over:
            # 更新
            all_sprites.update()

            # 新しい土管の生成
            # 最も右にある土管のX座標を確認
            rightmost_pipe_x = max([p.rect.x for p in pipes_group]) if len(pipes_group) > 0 else 0
            if rightmost_pipe_x < SCREEN_WIDTH - 200:
                # すぐに all_sprites にも追加するため一時リストを受け取る
                new_pipes = []
                # spawn_pipes 関数をインライン展開するか、追加したものを取得する
                gap_y = random.randint(50, SCREEN_HEIGHT - 50 - 100 - PIPE_GAP)
                top_pipe = Pipe(SCREEN_WIDTH, gap_y, is_top=True)
                bottom_pipe = Pipe(SCREEN_WIDTH, gap_y + PIPE_GAP, is_top=False)
                pipes_group.add(top_pipe, bottom_pipe)
                all_sprites.add(top_pipe, bottom_pipe)

            # スコア加算
            for pipe in pipes_group:
                # 上の土管だけを基準にスコアを加算（二重加算防止）
                if pipe.is_top and not pipe.passed and bird.rect.centerx > pipe.rect.centerx:
                    score += 1
                    pipe.passed = True

            # --- 衝突判定 ---
            # 画面外（上下）
            ground_y = SCREEN_HEIGHT - 50
            if bird.rect.top < 0 or bird.rect.bottom > ground_y:
                game_over = True

            # 土管との衝突
            if pygame.sprite.spritecollide(bird, pipes_group, False):
                game_over = True

        # --- 描画 ---
        screen.fill(SKY_BLUE)

        # すべてのスプライトを描画
        # all_sprites.draw(screen) だと重なり順が不定になる可能性があるため、土管→鳥の順で描画
        pipes_group.draw(screen)
        screen.blit(bird.image, bird.rect)

        # 地面（手前に描画）
        pygame.draw.rect(screen, GROUND_COLOR, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))

        # スコア表示
        score_text = font.render(str(score), True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 50))

        # ゲームオーバー表示
        if game_over:
            go_text = font.render("Game Over", True, WHITE)
            screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, SCREEN_HEIGHT // 2))
            retry_text = font.render("Press SPACE", True, WHITE)
            screen.blit(retry_text, (SCREEN_WIDTH // 2 - retry_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
