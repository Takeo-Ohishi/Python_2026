import pygame
import sys
import os

# 画面設定
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 色の定義 (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
SKY_BLUE = (135, 206, 235)

# プレイヤー設定
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 40
PLAYER_SPEED = 5
PLAYER_JUMP_FORCE = -15
GRAVITY = 0.8
MAX_FALL_SPEED = 12

# ゴール設定
GOAL_WIDTH = 50
GOAL_HEIGHT = 50

# プレイヤーの画像ファイル
BASE_DIR = os.path.dirname(__file__)
PLAYER_IMG_PATH1 = os.path.join(BASE_DIR, "costume1.png")
PLAYER_IMG_PATH2 = os.path.join(BASE_DIR, "costume2.png")

# 足場の配置（横に長いステージ）
platforms_data = [
    (0, SCREEN_HEIGHT - 40, 2500, 40), # 長い地面
    (150, 450, 100, 20),
    (350, 350, 100, 20),
    (550, 250, 150, 20),
    (800, 400, 100, 20),
    (1050, 300, 200, 20),
    (1350, 200, 100, 20),
    (1550, 250, 150, 20),
    (1800, 350, 150, 20)
]

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.img1 = pygame.image.load(PLAYER_IMG_PATH1).convert_alpha()
        self.img1 = pygame.transform.scale(self.img1, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.img2 = pygame.image.load(PLAYER_IMG_PATH2).convert_alpha()
        self.img2 = pygame.transform.scale(self.img2, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.img3 = pygame.image.load(PLAYER_IMG_PATH1).convert_alpha()
        self.img3 = pygame.transform.scale(self.img3, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.img3 = pygame.transform.flip(self.img3, True, False)
        self.img4 = pygame.image.load(PLAYER_IMG_PATH2).convert_alpha()
        self.img4 = pygame.transform.scale(self.img4, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.img4 = pygame.transform.flip(self.img4, True, False)
        self.frame_index = 0
        self.frame = [self.img1, self.img2 , self.img3, self.img4]
        self.image = self.frame[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.animation_clock = 0
        
        # 速度ベクトル
        self.vel_x = 0
        self.vel_y = 0

        # 状態
        self.on_ground = False

    def update(self):

        keys = pygame.key.get_pressed()
        self.vel_x = 0

        if keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED
        
        # ジャンプ
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            if self.on_ground:
                self.vel_y = PLAYER_JUMP_FORCE
                self.on_ground = False

        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        # アニメーション
        self.animation_clock += 1
        if self.animation_clock >= 10 and self.vel_x != 0:  # 10フレームごとにアニメーションを切り替える
            self.animation_clock = 0
            self.frame_index ^= 1  # フレームを切り替える
            if self.vel_x >0:
                self.image = self.frame[self.frame_index]  # 右向きのフレーム
            else:
                self.image = self.frame[self.frame_index + 2]  # 左向きのフレーム

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((GOAL_WIDTH, GOAL_HEIGHT))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Level:
    def __init__(self, player):
        self.player = player
        self.platforms = pygame.sprite.Group()
        self.goal = pygame.sprite.GroupSingle()
        self.is_cleared = False
        self.world_shift = 0

        for data in platforms_data:
            platform = Platform(*data)
            self.platforms.add(platform)

        # ゴールの配置（遠くに設定）
        goal_x = 2100
        goal_y = 250 - GOAL_HEIGHT
        self.goal.add(Goal(goal_x, goal_y))

    def scroll_x(self):
        player = self.player
        player_x = player.rect.centerx
        direction_x = player.vel_x

        # 画面の左から1/4、右から1/4の位置でスクロール
        if player_x < SCREEN_WIDTH // 4 and direction_x < 0:
            self.world_shift = -direction_x
            player.vel_x = 0
        elif player_x > SCREEN_WIDTH - (SCREEN_WIDTH // 4) and direction_x > 0:
            self.world_shift = -direction_x
            player.vel_x = 0
        else:
            self.world_shift = 0

    def update(self):
        self.scroll_x()
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        
        # スクロール量の適用
        for platform in self.platforms.sprites():
            platform.rect.x += self.world_shift
        self.goal.sprite.rect.x += self.world_shift

        self.check_goal()

    def horizontal_movement_collision(self):
        self.player.rect.x += self.player.vel_x
        
        for sprite in self.platforms.sprites():
            if sprite.rect.colliderect(self.player.rect):
                if self.player.vel_x > 0: # 右移動中
                    self.player.rect.right = sprite.rect.left
                elif self.player.vel_x < 0: # 左移動中
                    self.player.rect.left = sprite.rect.right

    def vertical_movement_collision(self):
        self.player.rect.y += self.player.vel_y
        self.player.on_ground = False

        for sprite in self.platforms.sprites():
            if sprite.rect.colliderect(self.player.rect):
                if self.player.vel_y > 0: # 落下中
                    self.player.rect.bottom = sprite.rect.top
                    self.player.vel_y = 0
                    self.player.on_ground = True
                elif self.player.vel_y < 0: # 上昇（ジャンプ）中
                    self.player.rect.top = sprite.rect.bottom
                    self.player.vel_y = 0

    def check_goal(self):
        if pygame.sprite.spritecollide(self.player, self.goal, False):
            self.is_cleared = True

    def draw(self, surface):
        self.platforms.draw(surface)
        self.goal.draw(surface)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simple Platformer")
    clock = pygame.time.Clock()

    player = Player(50, SCREEN_HEIGHT - 100)
    player_group = pygame.sprite.GroupSingle()
    player_group.add(player)

    level = Level(player)

    font = pygame.font.SysFont(None, 64)
    clear_text = font.render("GOAL!", True, RED)
    clear_rect = clear_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not level.is_cleared:
            player_group.update()
            level.update()

        # 描画
        screen.fill(SKY_BLUE)
        level.draw(screen)
        player_group.draw(screen)

        if level.is_cleared:
            screen.blit(clear_text, clear_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
