import pygame
import sys
import random

# 画面設定
WIDTH, HEIGHT = 870, 600

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# パステルカラー（淡い色）
PASTEL_RED = (255, 179, 186)
PASTEL_ORANGE = (255, 223, 186)
PASTEL_YELLOW = (255, 255, 186)
PASTEL_GREEN = (186, 255, 201)
PASTEL_CYAN = (204, 255, 255)
PASTEL_BLUE = (186, 225, 255)
PASTEL_PURPLE = (220, 200, 255)
PASTEL_PINK = (255, 204, 229)
colors = [PASTEL_RED, PASTEL_ORANGE, PASTEL_YELLOW, PASTEL_GREEN, PASTEL_CYAN, PASTEL_BLUE, PASTEL_PURPLE, PASTEL_PINK]

# パドル設定
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
PADDLE_SPEED = 7

# ボール設定
BALL_RADIUS = 10
BALL_SPEED_X = 5
BALL_SPEED_Y = -5

# ブロック設定
BLOCK_ROWS = 5
BLOCK_COLS = 10
BLOCK_WIDTH = 70
BLOCK_HEIGHT = 20
BLOCK_PADDING = 10
BLOCK_OFFSET_TOP = 50
BLOCK_OFFSET_LEFT = 35

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((BALL_RADIUS * 2, BALL_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed_x = BALL_SPEED_X * random.choice([1, -1])
        self.speed_y = BALL_SPEED_Y

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # 壁との衝突
        if self.rect.left <= 0:
            self.rect.left = 0
            self.speed_x *= -1
        if self.rect.right >= WIDTH:
            self.rect.right = WIDTH 
            self.speed_x *= -1
        if self.rect.top <= 0:
            self.rect.top = 0
            self.speed_y *= -1

class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PADDLE_WIDTH, PADDLE_HEIGHT))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 30

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += PADDLE_SPEED 

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ブロック崩し")
    # フォント設定
    font = pygame.font.SysFont(None, 48)
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()

    # パドルとボールの作成
    paddle = Paddle()
    ball = Ball()
    all_sprites.add(paddle)
    all_sprites.add(ball) 
    # ブロックの作成
    blocks = pygame.sprite.Group()
    for row in range(BLOCK_ROWS):
        for col in range(BLOCK_COLS):
            block_x = BLOCK_OFFSET_LEFT + col * (BLOCK_WIDTH + BLOCK_PADDING)
            block_y = BLOCK_OFFSET_TOP + row * (BLOCK_HEIGHT + BLOCK_PADDING)
            block = Block(block_x, block_y, colors[row % len(colors)])
            blocks.add(block)
            all_sprites.add(block)

    score = 0
    state = "PLAYING" # "PLAYING", "GAME_OVER", "CLEAR"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and state != "PLAYING":
                    # スペースキーでリスタート
                    main()
                    return

        all_sprites.update()

        # ボールとパドルの衝突
        if pygame.sprite.collide_rect(ball, paddle):
            ball.speed_y *= -1
            # パドルのどこに当たったかで反射角（速度）を少し変える
            hit_pos = (ball.rect.centerx - paddle.rect.centerx) / (PADDLE_WIDTH / 2)
            ball.speed_x = BALL_SPEED_X * hit_pos

        # ボールとブロックの衝突
        block_hit_list = pygame.sprite.spritecollide(ball, blocks, True)
        if block_hit_list:
            score += len(block_hit_list) * 10
            ball.speed_y *= -1

        screen.fill(BLACK)

        # クリア判定
        is_clear = True
        for block in blocks:
            is_clear = False
            break
        if is_clear:
            state = "CLEAR" 

        if ball.rect.bottom >= HEIGHT:
            state = "GAME_OVER"

        all_sprites.draw(screen)

        # スコア描画
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # ゲーム状態ごとのメッセージ描画
        if state == "GAME_OVER":
            draw_text("GAME OVER", font, RED, screen, WIDTH // 2, HEIGHT // 2)
            draw_text("Press SPACE to Restart", pygame.font.SysFont(None, 36), WHITE, screen, WIDTH // 2, HEIGHT // 2 + 50)
        elif state == "CLEAR":
            draw_text("GAME CLEAR!", font, GREEN, screen, WIDTH // 2, HEIGHT // 2)
            draw_text("Press SPACE to Restart", pygame.font.SysFont(None, 36), WHITE, screen, WIDTH // 2, HEIGHT // 2 + 50)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()