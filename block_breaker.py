import pygame
import sys
import random

# 初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 870, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ブロック崩し")

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

# フォント設定
font = pygame.font.SysFont(None, 48)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def main():
    clock = pygame.time.Clock()

    # パドルの初期位置
    paddle = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 50, PADDLE_WIDTH, PADDLE_HEIGHT)

    # ボールの初期位置
    ball = pygame.Rect(WIDTH // 2 - BALL_RADIUS, HEIGHT // 2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
    ball_speed_x = BALL_SPEED_X * random.choice([1, -1])
    ball_speed_y = BALL_SPEED_Y

    # ブロックの作成
    blocks = []
    # 淡い色のリスト
    colors = [PASTEL_RED, PASTEL_ORANGE, PASTEL_YELLOW, PASTEL_GREEN, PASTEL_CYAN, PASTEL_BLUE, PASTEL_PURPLE, PASTEL_PINK]
    for row in range(BLOCK_ROWS):
        block_row = []
        for col in range(BLOCK_COLS):
            x = BLOCK_OFFSET_LEFT + col * (BLOCK_WIDTH + BLOCK_PADDING)
            y = BLOCK_OFFSET_TOP + row * (BLOCK_HEIGHT + BLOCK_PADDING)
            rect = pygame.Rect(x, y, BLOCK_WIDTH, BLOCK_HEIGHT)
            # 列 (col) ごとに色を変える
            block_row.append((rect, colors[col % len(colors)]))
        blocks.append(block_row)

    score = 0
    state = "PLAYING" # "PLAYING", "GAME_OVER", "CLEAR"

    while True:
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and state != "PLAYING":
                    # スペースキーでリスタート
                    main()
                    return

        keys = pygame.key.get_pressed()

        if state == "PLAYING":
            # パドルの移動
            if keys[pygame.K_LEFT] and paddle.left > 0:
                paddle.x -= PADDLE_SPEED
            if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
                paddle.x += PADDLE_SPEED

            # ボールの移動
            ball.x += ball_speed_x
            ball.y += ball_speed_y

            # 壁との衝突
            if ball.left <= 0 or ball.right >= WIDTH:
                ball_speed_x *= -1
            if ball.top <= 0:
                ball_speed_y *= -1

            # パドルとの衝突
            if ball.colliderect(paddle) and ball_speed_y > 0:
                ball_speed_y *= -1
                # パドルのどこに当たったかで反射角（速度）を少し変える
                hit_pos = (ball.centerx - paddle.centerx) / (PADDLE_WIDTH / 2)
                ball_speed_x = BALL_SPEED_X * hit_pos

            # ボールが落ちた場合
            if ball.bottom >= HEIGHT:
                state = "GAME_OVER"

            # ブロックとの衝突
            block_hit = False
            for row in blocks:
                for item in row:
                    rect, color = item
                    if ball.colliderect(rect):
                        ball_speed_y *= -1
                        row.remove(item)
                        score += 10
                        block_hit = True
                        break
                if block_hit:
                    break
            
            # クリア判定
            is_clear = True
            for row in blocks:
                if len(row) > 0:
                    is_clear = False
                    break
            if is_clear:
                state = "CLEAR"

        # 描画
        screen.fill(BLACK)

        # パドル描画
        pygame.draw.rect(screen, BLUE, paddle)

        # ボール描画
        pygame.draw.circle(screen, WHITE, ball.center, BALL_RADIUS)

        # ブロック描画
        for row in blocks:
            for item in row:
                rect, color = item
                pygame.draw.rect(screen, color, rect)

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
