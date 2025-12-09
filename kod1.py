import pygame
import math
import numpy as np
import heapq
import random

# --- AYARLAR ---
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
COLS, ROWS = WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE
ROBOT_RADIUS = 9 
SENSING_RADIUS = 100

# Durum Kodları (Matris için)
VAL_UNKNOWN = 2  # Bilinmeyen
VAL_FREE = 1     # Boş Alan
VAL_WALL = 0     # Duvar

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)      # Duvar ve Arka Plan
GRAY = (200, 200, 200) # Keşfedilmiş Boş Alan
RED = (255, 0, 0)      # Robot ve Sensör Menzili (Kenarlık)
BLUE = (0, 0, 255)     # Yol
GREEN = (0, 255, 0)    # Mesaj

class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 3
        self.path = []

    def check_collision(self, new_x, new_y, grid):
        grid_x = int(new_x // GRID_SIZE)
        grid_y = int(new_y // GRID_SIZE)

        if not (0 <= grid_x < COLS and 0 <= grid_y < ROWS):
            return True 
        if grid[grid_x][grid_y] == VAL_WALL:
            return True 
        return False

    def move(self, real_map):
        if self.path:
            target_node = self.path[0]
            target_x = target_node[0] * GRID_SIZE + GRID_SIZE // 2
            target_y = target_node[1] * GRID_SIZE + GRID_SIZE // 2
            
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)
            
            if dist < self.speed:
                self.x = target_x
                self.y = target_y
                self.path.pop(0)
            else:
                self.angle = math.atan2(dy, dx)
                next_x = self.x + math.cos(self.angle) * self.speed
                next_y = self.y + math.sin(self.angle) * self.speed
                if not self.check_collision(next_x, next_y, real_map):
                    self.x = next_x
                    self.y = next_y
        else:
            keys = pygame.key.get_pressed()
            new_x, new_y = self.x, self.y
            moved = False

            if keys[pygame.K_LEFT]: new_x -= self.speed; moved = True
            if keys[pygame.K_RIGHT]: new_x += self.speed; moved = True
            if keys[pygame.K_UP]: new_y -= self.speed; moved = True
            if keys[pygame.K_DOWN]: new_y += self.speed; moved = True

            if moved and not self.check_collision(new_x, new_y, real_map):
                self.x = new_x
                self.y = new_y

        self.x = max(ROBOT_RADIUS, min(WIDTH - ROBOT_RADIUS, self.x))
        self.y = max(ROBOT_RADIUS, min(HEIGHT - ROBOT_RADIUS, self.y))

    def draw(self, win):
        pygame.draw.circle(win, RED, (int(self.x), int(self.y)), ROBOT_RADIUS)
        if self.path:
            points = [(n[0]*GRID_SIZE + GRID_SIZE//2, n[1]*GRID_SIZE + GRID_SIZE//2) for n in self.path]
            if len(points) > 1:
                pygame.draw.lines(win, BLUE, False, points, 3)

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(grid, start, goal):
    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)] 
    close_set = set()
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    oheap = []
    heapq.heappush(oheap, (f_score[start], start))

    while oheap:
        current = heapq.heappop(oheap)[1]
        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return data[::-1]
        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            if 0 <= neighbor[0] < COLS and 0 <= neighbor[1] < ROWS:
                if grid[neighbor[0]][neighbor[1]] != VAL_FREE: continue
            else: continue
            tentative_g_score = g_score[current] + 1
            if neighbor in close_set and tentative_g_score >= g_score.get(neighbor, 0): continue
            if tentative_g_score < g_score.get(neighbor, float('inf')) or neighbor not in [i[1] for i in oheap]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (f_score[neighbor], neighbor))
    return []

def generate_island_map(cols, rows):
    """Büyük adacıklı harita oluşturur"""
    grid = np.ones((cols, rows)) * VAL_FREE 
    
    # Çerçeve
    grid[0:cols, 0] = VAL_WALL
    grid[0:cols, rows-1] = VAL_WALL
    grid[0, 0:rows] = VAL_WALL
    grid[cols-1, 0:rows] = VAL_WALL

    num_islands = 7
    for _ in range(num_islands):
        w = random.randint(5, 12) 
        h = random.randint(5, 12)
        x = random.randint(3, cols - 15)
        y = random.randint(3, rows - 15)
        
        if x < 10 and y < 10: continue
        grid[x:x+w, y:y+h] = VAL_WALL

    return grid

def save_scanned_matrix(grid, filename="taranan_alan.txt"):
    """Sadece robotun 'known_map' matrisini kaydeder."""
    cols = len(grid)
    rows = len(grid[0])
    
    with open(filename, "w") as f:
        f.write(f"# Harita Boyutu: {cols}x{rows}\n")
        f.write("# 2: Bilinmeyen, 1: Boş, 0: Duvar\n")
        for y in range(rows):
            line = []
            for x in range(cols):
                val = int(grid[x][y])
                line.append(str(val))
            f.write(" ".join(line) + "\n")
    
    print(f"TARANAN matris kaydedildi: {filename}")

def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Robot: Siyah Engeller & Kırmızı Menzil")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 20)

    # Gerçek Harita
    real_world_map = generate_island_map(COLS, ROWS)
    # Robotun Hafızası
    known_map = np.full((COLS, ROWS), VAL_UNKNOWN) 

    robot = Robot(50, 50)

    running = True
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Kayıt (S)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_scanned_matrix(known_map, "taranan_alan.txt")

            # Navigasyon
            if event.type == pygame.MOUSEBUTTONDOWN:
                m_x, m_y = pygame.mouse.get_pos()
                target_grid = (m_x // GRID_SIZE, m_y // GRID_SIZE)
                start_grid = (int(robot.x) // GRID_SIZE, int(robot.y) // GRID_SIZE)
                
                if 0 <= target_grid[0] < COLS and 0 <= target_grid[1] < ROWS:
                    if known_map[target_grid[0]][target_grid[1]] == VAL_FREE:
                        print("Rota hesaplanıyor...")
                        path = a_star_search(known_map, start_grid, target_grid)
                        if path: robot.path = path
                        else: print("Yol yok.")
                    else:
                        print("Hedef bilinmiyor veya duvar.")

        robot.move(real_world_map)

        # Haritalama (Sensör)
        r_grid_x = int(robot.x) // GRID_SIZE
        r_grid_y = int(robot.y) // GRID_SIZE
        view_range = 4
        for i in range(-view_range, view_range + 1):
            for j in range(-view_range, view_range + 1):
                nx, ny = r_grid_x + i, r_grid_y + j
                if 0 <= nx < COLS and 0 <= ny < ROWS:
                    known_map[nx][ny] = real_world_map[nx][ny]

        # --- ÇİZİM ---
        win.fill(BLACK) # Arka plan (Bilinmeyen = Siyah)
        
        for x in range(COLS):
            for y in range(ROWS):
                rect = (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                val = known_map[x][y]
                
                # 1. Boş Alanları Çiz (Gri)
                if val == VAL_FREE: 
                    pygame.draw.rect(win, GRAY, rect)
                    pygame.draw.rect(win, WHITE, rect, 1) # Izgara çizgisi
                
                # 2. Duvarları Çiz (SİYAH - Arka planla aynı)
                elif val == VAL_WALL:
                    # Zaten arka plan siyah olduğu için rect fill yapmaya gerek yok,
                    # ama kodun okunabilirliği için açıkça siyah basıyoruz.
                    pygame.draw.rect(win, BLACK, rect)
                    
                    # 3. MENZİL GÖSTERİMİ (Önemli Kısım)
                    # Eğer bu duvar robotun sensör menzilindeyse, üstüne kırmızı çerçeve çiz.
                    # Bu sayede engel siyah kalır ama robotun onu gördüğü belli olur.
                    dist_x = abs(x - r_grid_x)
                    dist_y = abs(y - r_grid_y)
                    
                    if real_world_map[x][y] == VAL_WALL: # Gerçekten duvar mı?
                        if dist_x <= view_range and dist_y <= view_range:
                             # Engelin üzerine Kırmızı Kenarlık Çiz (İçi boş, sadece çerçeve)
                             pygame.draw.rect(win, RED, rect, 1)

        robot.draw(win)
        
        text = font.render("'S' tuşu: Matris Kaydet", True, GREEN)
        win.blit(text, (10, 10))
        
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()