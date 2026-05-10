import pygame
import math
import random
import sys

# --- 定数 ---
WIDTH, HEIGHT = 800, 600
MAP_WIDTH = 600
UI_WIDTH = 200
FPS = 60

# 色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
DARK_GRAY = (100, 100, 100)
UI_BG = (50, 50, 60)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
YELLOW = (255, 200, 50)
ROAD_COLOR = (180, 160, 120)
GRASS_COLOR = (100, 180, 100)

# ルート定義（ウェイポイント）
ROUTE_1 = [(0, 100), (200, 100), (200, 300), (400, 300), (400, 100), (600, 100)] # 上ルート
ROUTE_2 = [(0, 300), (100, 300), (100, 500), (500, 500), (500, 300), (600, 300)] # 中央下ルート
ROUTE_3 = [(0, 500), (300, 500), (300, 400), (200, 400), (200, 200), (600, 200)] # 下から上ルート
ROUTES = [ROUTE_1, ROUTE_2, ROUTE_3]

# --- クラス ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, route, hp, speed, reward):
        super().__init__()
        self.route = route
        self.target_idx = 1
        self.x, self.y = self.route[0]
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (10, 10), 10)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
        self.max_hp = hp
        self.hp = hp
        self.speed = speed
        self.reward = reward
        self.reached_base = False

    def update(self):
        if self.target_idx < len(self.route):
            tx, ty = self.route[self.target_idx]
            dx, dy = tx - self.x, ty - self.y
            dist = math.hypot(dx, dy)
            
            if dist < self.speed:
                self.x, self.y = tx, ty
                self.target_idx += 1
            else:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
            self.rect.center = (int(self.x), int(self.y))
        else:
            self.reached_base = True
            self.kill()

    def draw_hp(self, surface):
        hp_ratio = max(0, self.hp / self.max_hp)
        bar_width = 20
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 8, bar_width, 4))
        pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 8, bar_width * hp_ratio, 4))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target, damage, speed, color=YELLOW):
        super().__init__()
        self.x, self.y = x, y
        self.target = target
        self.damage = damage
        self.speed = speed
        
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (4, 4), 4)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        if not self.target.alive():
            self.kill()
            return
            
        tx, ty = self.target.rect.center
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        
        if dist < self.speed:
            self.target.hp -= self.damage
            if self.target.hp <= 0:
                self.target.kill()
            self.kill()
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            self.rect.center = (int(self.x), int(self.y))

class Tower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x, self.y = x, y
        self.level = 1
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.cooldown_counter = 0

        # これらのパラメータはサブクラスで上書きされる
        self.range = 100
        self.damage = 10
        self.cooldown_max = 60
        self.color = WHITE
        self.bullet_color = YELLOW
        self.bullet_speed = 10

    def update(self, enemies, bullets_group):
        if self.cooldown_counter > 0:
            self.cooldown_counter -= 1
        else:
            target = self.find_target(enemies)
            if target:
                self.shoot(target, bullets_group)
                self.cooldown_counter = self.cooldown_max

    def find_target(self, enemies):
        # 範囲内にいる敵の中で最も進んでいる（拠点に近い）敵を狙う簡易ロジック
        closest_enemy = None
        min_dist = float('inf')
        for enemy in enemies:
            dist = math.hypot(enemy.rect.centerx - self.x, enemy.rect.centery - self.y)
            if dist <= self.range:
                if dist < min_dist:
                    min_dist = dist
                    closest_enemy = enemy
        return closest_enemy

    def shoot(self, target, bullets_group):
        bullet = Bullet(self.x, self.y, target, self.damage, self.bullet_speed, self.bullet_color)
        bullets_group.add(bullet)

class BasicTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.range = 120
        self.damage = 25
        self.cooldown_max = 60 # 1秒に1回
        self.color = BLUE
        pygame.draw.rect(self.image, self.color, (0, 0, 30, 30))
        pygame.draw.rect(self.image, DARK_GRAY, (0, 0, 30, 30), 2)

class SniperTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.range = 250
        self.damage = 100
        self.cooldown_max = 120 # 2秒に1回
        self.color = RED
        self.bullet_color = RED
        self.bullet_speed = 15
        pygame.draw.circle(self.image, self.color, (15, 15), 15)
        pygame.draw.circle(self.image, DARK_GRAY, (15, 15), 15, 2)

class RapidTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.range = 90
        self.damage = 5
        self.cooldown_max = 10 # 0.16秒に1回
        self.color = GREEN
        self.bullet_color = GREEN
        points = [(15, 0), (0, 30), (30, 30)]
        pygame.draw.polygon(self.image, self.color, points)
        pygame.draw.polygon(self.image, DARK_GRAY, points, 2)

# --- メインロジック ---
def draw_routes(surface):
    for route in ROUTES:
        if len(route) > 1:
            pygame.draw.lines(surface, ROAD_COLOR, False, route, 40)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tower Defense")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    large_font = pygame.font.SysFont(None, 48)

    # ゲーム状態
    money = 200
    base_hp = 20
    wave = 1
    spawn_timer = 0
    enemies_to_spawn = 5
    spawn_delay = 60
    
    # 資金強化システム
    income_level = 0
    income_cost = 100
    passive_income_timer = 0

    # グループ
    enemies = pygame.sprite.Group()
    towers = pygame.sprite.Group()
    bullets = pygame.sprite.Group()

    # UI用のボタン定義
    towers_info = [
        {"class": BasicTower, "name": "Basic (Blue)", "cost": 50, "color": BLUE},
        {"class": SniperTower, "name": "Sniper (Red)", "cost": 120, "color": RED},
        {"class": RapidTower, "name": "Rapid (Green)", "cost": 80, "color": GREEN}
    ]
    selected_tower_idx = None

    running = True
    game_over = False

    while running:
        # 1. イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                
                # UIエリアのクリック処理
                if mx > MAP_WIDTH:
                    # タワー選択ボタン
                    for i, info in enumerate(towers_info):
                        btn_rect = pygame.Rect(MAP_WIDTH + 10, 100 + i * 80, 180, 60)
                        if btn_rect.collidepoint(mx, my):
                            selected_tower_idx = i
                    
                    # 資金強化ボタン
                    upgrade_rect = pygame.Rect(MAP_WIDTH + 10, 360, 180, 60)
                    if upgrade_rect.collidepoint(mx, my) and money >= income_cost:
                        money -= income_cost
                        income_level += 1
                        income_cost = int(income_cost * 1.5)
                
                # マップエリアのクリック処理（タワー配置）
                elif not game_over and selected_tower_idx is not None:
                    info = towers_info[selected_tower_idx]
                    if money >= info["cost"]:
                        # 既存のタワーや道の上には置けない判定（簡易）
                        # ルートとの距離チェック
                        can_place = True
                        for route in ROUTES:
                            for i in range(len(route) - 1):
                                p1, p2 = route[i], route[i+1]
                                # 線分と点の距離の簡易判定
                                cx, cy = max(min(mx, max(p1[0], p2[0])), min(p1[0], p2[0])), max(min(my, max(p1[1], p2[1])), min(p1[1], p2[1]))
                                if math.hypot(mx - cx, my - cy) < 25:
                                    can_place = False
                        
                        for tower in towers:
                            if math.hypot(mx - tower.x, my - tower.y) < 30:
                                can_place = False
                        
                        if can_place:
                            money -= info["cost"]
                            new_tower = info["class"](mx, my)
                            towers.add(new_tower)
                            selected_tower_idx = None # 配置したら選択解除

        if not game_over:
            # 2. ロジック更新
            # パッシブ収入
            passive_income_timer += 1
            if passive_income_timer >= 60: # 1秒ごと
                money += income_level * 2
                passive_income_timer = 0

            # 敵のスポーン
            if enemies_to_spawn > 0:
                spawn_timer += 1
                if spawn_timer >= spawn_delay:
                    route = random.choice(ROUTES)
                    hp = 50 + (wave * 15)
                    speed = 1.0 + (wave * 0.1)
                    reward = 10 + wave
                    enemy = Enemy(route, hp, speed, reward)
                    enemies.add(enemy)
                    enemies_to_spawn -= 1
                    spawn_timer = 0
            elif len(enemies) == 0:
                # ウェーブクリア
                wave += 1
                enemies_to_spawn = 5 + int(wave * 1.5)
                spawn_delay = max(20, 60 - wave * 2)
                money += 50 + (wave * 10) # ウェーブクリアボーナス

            # 敵の更新（基地到達と撃破判定）
            for enemy in enemies.sprites():
                enemy.update()
                if enemy.reached_base:
                    base_hp -= 1
                    if base_hp <= 0:
                        game_over = True
                elif enemy.hp <= 0:
                    money += enemy.reward

            towers.update(enemies, bullets)
            bullets.update()

        # 3. 描画
        screen.fill(GRASS_COLOR)
        
        # マップ描画
        draw_routes(screen)
        
        # オブジェクト描画
        towers.draw(screen)
        for enemy in enemies:
            screen.blit(enemy.image, enemy.rect)
            enemy.draw_hp(screen)
        bullets.draw(screen)

        # 拠点（ベース）描画
        pygame.draw.rect(screen, DARK_GRAY, (MAP_WIDTH - 20, 0, 20, HEIGHT))

        # UIエリア描画
        pygame.draw.rect(screen, UI_BG, (MAP_WIDTH, 0, UI_WIDTH, HEIGHT))
        pygame.draw.line(screen, WHITE, (MAP_WIDTH, 0), (MAP_WIDTH, HEIGHT), 2)

        # ステータス表示
        txt_hp = font.render(f"Base HP: {base_hp}", True, RED)
        txt_money = font.render(f"Money: ${money}", True, YELLOW)
        txt_wave = font.render(f"Wave: {wave}", True, WHITE)
        screen.blit(txt_hp, (MAP_WIDTH + 10, 10))
        screen.blit(txt_money, (MAP_WIDTH + 10, 40))
        screen.blit(txt_wave, (MAP_WIDTH + 10, 70))

        # タワー購入ボタン
        for i, info in enumerate(towers_info):
            btn_rect = pygame.Rect(MAP_WIDTH + 10, 100 + i * 80, 180, 60)
            color = GRAY if money >= info["cost"] else DARK_GRAY
            border_color = WHITE if selected_tower_idx == i else BLACK
            
            pygame.draw.rect(screen, color, btn_rect)
            pygame.draw.rect(screen, border_color, btn_rect, 3)
            
            # タワーのアイコン
            pygame.draw.rect(screen, info["color"], (MAP_WIDTH + 20, 115 + i * 80, 30, 30))
            
            txt_name = font.render(info["name"].split(" ")[0], True, BLACK)
            txt_cost = font.render(f"${info['cost']}", True, BLACK)
            screen.blit(txt_name, (MAP_WIDTH + 60, 110 + i * 80))
            screen.blit(txt_cost, (MAP_WIDTH + 60, 135 + i * 80))

        # 資金強化ボタン
        upgrade_rect = pygame.Rect(MAP_WIDTH + 10, 360, 180, 60)
        u_color = YELLOW if money >= income_cost else DARK_GRAY
        pygame.draw.rect(screen, u_color, upgrade_rect)
        pygame.draw.rect(screen, BLACK, upgrade_rect, 3)
        txt_u1 = font.render("Income Upgrade", True, BLACK)
        txt_u2 = font.render(f"Cost: ${income_cost}", True, BLACK)
        txt_u3 = font.render(f"Lv: {income_level} (+{income_level*2}/s)", True, BLACK)
        screen.blit(txt_u1, (MAP_WIDTH + 20, 365))
        screen.blit(txt_u2, (MAP_WIDTH + 20, 385))
        screen.blit(txt_u3, (MAP_WIDTH + 20, 405))

        # ゲームオーバー表示
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            txt_go = large_font.render("GAME OVER", True, RED)
            screen.blit(txt_go, (WIDTH//2 - txt_go.get_width()//2, HEIGHT//2))

        # カーソルにタワーを追従（選択中）
        if selected_tower_idx is not None and not game_over:
            mx, my = pygame.mouse.get_pos()
            if mx < MAP_WIDTH:
                info = towers_info[selected_tower_idx]
                # 半透明で描画
                temp_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
                temp_surface.fill((*info["color"], 128))
                screen.blit(temp_surface, (mx - 15, my - 15))
                # 射程円
                # タワーのインスタンスを一時的に作るのはコストがかかるのでハードコードか取得
                range_r = 120 if selected_tower_idx == 0 else (250 if selected_tower_idx == 1 else 90)
                pygame.draw.circle(screen, (*WHITE, 50), (mx, my), range_r, 1)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
