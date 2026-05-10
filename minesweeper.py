import pygame
import random
import sys

# --- 設定 ---
CELL_SIZE = 25
ROWS = 20
COLS = 20
MINES = 50
HEADER_HEIGHT = 60

WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE + HEADER_HEIGHT

# 色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (192, 192, 192)
DARK_GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)

# Pygame初期化
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")
font = pygame.font.SysFont("Arial", 20, bold=True)
large_font = pygame.font.SysFont("Arial", 36, bold=True)

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.neighbor_mines = 0

class Minesweeper:
    def __init__(self):
        self.grid = [[Cell(r, c) for c in range(COLS)] for r in range(ROWS)]
        self.first_click = True
        self.game_over = False
        self.game_won = False
        self.flags_placed = 0

    def place_mines(self, first_r, first_c):
        mines_placed = 0
        while mines_placed < MINES:
            r = random.randint(0, ROWS - 1)
            c = random.randint(0, COLS - 1)
            # 最初のクリック位置と既に地雷がある場所には配置しない
            if not self.grid[r][c].is_mine and (r != first_r or c != first_c):
                self.grid[r][c].is_mine = True
                mines_placed += 1
        self.calculate_neighbors()

    def calculate_neighbors(self):
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c].is_mine:
                    continue
                count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < ROWS and 0 <= nc < COLS and self.grid[nr][nc].is_mine:
                            count += 1
                self.grid[r][c].neighbor_mines = count

    def reveal(self, r, c):
        if self.game_over or self.game_won:
            return
        if not (0 <= r < ROWS and 0 <= c < COLS):
            return
        cell = self.grid[r][c]
        if cell.is_revealed or cell.is_flagged:
            return

        if self.first_click:
            self.place_mines(r, c)
            self.first_click = False

        cell.is_revealed = True

        if cell.is_mine:
            self.game_over = True
            self.reveal_all_mines()
            return

        if cell.neighbor_mines == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    self.reveal(r + dr, c + dc)
                    
        self.check_win()

    def toggle_flag(self, r, c):
        if self.game_over or self.game_won or self.first_click:
            return
        cell = self.grid[r][c]
        if not cell.is_revealed:
            if cell.is_flagged:
                cell.is_flagged = False
                self.flags_placed -= 1
            else:
                cell.is_flagged = True
                self.flags_placed += 1

    def check_win(self):
        for r in range(ROWS):
            for c in range(COLS):
                cell = self.grid[r][c]
                if not cell.is_mine and not cell.is_revealed:
                    return
        self.game_won = True
        self.reveal_all_mines(won=True)

    def reveal_all_mines(self, won=False):
        for r in range(ROWS):
            for c in range(COLS):
                cell = self.grid[r][c]
                if cell.is_mine:
                    cell.is_revealed = True
                    if won:
                        cell.is_flagged = True

    def draw(self):
        screen.fill(WHITE)
        
        # ヘッダー描画
        header_rect = pygame.Rect(0, 0, WIDTH, HEADER_HEIGHT)
        pygame.draw.rect(screen, DARK_GRAY, header_rect)
        status_text = f"Mines: {MINES - self.flags_placed}"
        if self.game_over:
            status_text = "GAME OVER"
        elif self.game_won:
            status_text = "YOU WIN!"
            
        text_surf = large_font.render(status_text, True, WHITE)
        screen.blit(text_surf, (WIDTH // 2 - text_surf.get_width() // 2, HEADER_HEIGHT // 2 - text_surf.get_height() // 2))

        # 盤面描画
        for r in range(ROWS):
            for c in range(COLS):
                cell = self.grid[r][c]
                rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE + HEADER_HEIGHT, CELL_SIZE, CELL_SIZE)
                
                if not cell.is_revealed:
                    pygame.draw.rect(screen, GRAY, rect)
                    pygame.draw.rect(screen, WHITE, rect, 2, border_top_left_radius=2)
                    pygame.draw.rect(screen, DARK_GRAY, rect, 2, border_bottom_right_radius=2)
                    if cell.is_flagged:
                        # 旗の描画
                        pygame.draw.polygon(screen, RED, [
                            (rect.x + CELL_SIZE//2, rect.y + CELL_SIZE//4),
                            (rect.x + CELL_SIZE//2, rect.y + CELL_SIZE*3//4),
                            (rect.x + CELL_SIZE*3//4, rect.y + CELL_SIZE//2)
                        ])
                        pygame.draw.line(screen, BLACK, (rect.x + CELL_SIZE//2, rect.y + CELL_SIZE//4), (rect.x + CELL_SIZE//2, rect.y + CELL_SIZE*3//4), 2)
                else:
                    pygame.draw.rect(screen, WHITE, rect)
                    pygame.draw.rect(screen, DARK_GRAY, rect, 1)
                    if cell.is_mine:
                        # 地雷の描画
                        pygame.draw.circle(screen, BLACK, (rect.x + CELL_SIZE//2, rect.y + CELL_SIZE//2), CELL_SIZE//4)
                        if self.game_over and not cell.is_flagged: 
                             # 踏んだ地雷などは背景を少し赤くする
                             pass # (簡略化)
                    elif cell.neighbor_mines > 0:
                        colors = [None, BLUE, GREEN, RED, (0, 0, 128), (128, 0, 0), (0, 128, 128), BLACK, DARK_GRAY]
                        num_text = font.render(str(cell.neighbor_mines), True, colors[cell.neighbor_mines])
                        screen.blit(num_text, (rect.x + CELL_SIZE//2 - num_text.get_width()//2, rect.y + CELL_SIZE//2 - num_text.get_height()//2))

def main():
    clock = pygame.time.Clock()
    game = Minesweeper()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r: # リセット
                    game = Minesweeper()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[1] < HEADER_HEIGHT:
                    # ヘッダー部分をクリックでリスタート
                    game = Minesweeper()
                    continue

                c = event.pos[0] // CELL_SIZE
                r = (event.pos[1] - HEADER_HEIGHT) // CELL_SIZE
                
                if event.button == 1: # 左クリック
                    game.reveal(r, c)
                elif event.button == 3: # 右クリック
                    game.toggle_flag(r, c)

        game.draw()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
