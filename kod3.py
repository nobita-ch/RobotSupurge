import pygame
import math
import numpy as np
import heapq
import random

# --- AYARLAR ---
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
COLS, ROWS = WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE
ROBOT_RADIUS = 10

# Hedef Keşif Oranı (%100 keşfedilince durur)
EXPLORATION_GOAL = 0.99 + 0.01 

# Renkler
UNKNOWN_COLOR = (240, 230, 140) 
FREE_COLOR = (200, 200, 200)    
WALL_COLOR = (0, 0, 0)          
ROBOT_COLOR = (255, 0, 0)       
PATH_COLOR = (0, 0, 255)        
TEXT_COLOR = (0, 100, 0)       
INFO_COLOR = (50, 50, 255)      

# Durum Kodları
VAL_UNKNOWN = 2
VAL_FREE = 1
VAL_WALL = 0

class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = 8 # Hızı biraz artırdım, daha çabuk bitirsin
        self.path = []
        self.mode = "EXPLORE"

    def auto_explore(self, grid):
        """Kusurlu Sekme Mantığı (Rastgele Sapmalı)"""
        dx = math.cos(self.angle) * self.speed
        dy = math.sin(self.angle) * self.speed

        next_x = self.x + dx
        next_y = self.y + dy

        next_grid_x = int(np.clip(next_x // GRID_SIZE, 0, COLS - 1))
        next_grid_y = int(np.clip(next_y // GRID_SIZE, 0, ROWS - 1))
        curr_grid_y = int(np.clip(self.y // GRID_SIZE, 0, ROWS - 1))

        hit = False

        # --- SINIRLARA ÇARPMA ---
        if next_x - ROBOT_RADIUS < 0 or next_x + ROBOT_RADIUS > WIDTH:
            dx = -dx
            hit = True
        
        if next_y - ROBOT_RADIUS < 0 or next_y + ROBOT_RADIUS > HEIGHT:
            dy = -dy
            hit = True

        # --- DUVARLARA ÇARPMA ---
        if not hit:
            if grid[next_grid_x][next_grid_y] == VAL_WALL:
                hit = True
                check_x = int((self.x + dx) // GRID_SIZE)
                if 0 <= check_x < COLS and grid[check_x][curr_grid_y] == VAL_WALL:
                    dx = -dx
                else:
                    dy = -dy 

        # --- AÇIYA RASTGELELİK EKLEME ---
        if hit:
            base_angle = math.atan2(dy, dx)
            noise = random.uniform(-0.35, 0.35) 
            self.angle = base_angle + noise
        else:
            self.angle = math.atan2(dy, dx)

        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.x = max(ROBOT_RADIUS, min(WIDTH - ROBOT_RADIUS, self.x))
        self.y = max(ROBOT_RADIUS, min(HEIGHT - ROBOT_RADIUS, self.y))

    def navigate(self):
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
                if not self.path:
                    # Hedefe varınca tekrar beklemeye geçsin
                    self.mode = "WAITING"
            else:
                angle_to = math.atan2(dy, dx)
                self.x += math.cos(angle_to) * self.speed
                self.y += math.sin(angle_to) * self.speed

    def draw(self, win):
        pygame.draw.circle(win, ROBOT_COLOR, (int(self.x), int(self.y)), ROBOT_RADIUS)
        if self.path:
            points = [(n[0]*GRID_SIZE + GRID_SIZE//2, n[1]*GRID_SIZE + GRID_SIZE//2) for n in self.path]
            if len(points) > 1:
                pygame.draw.lines(win, PATH_COLOR, False, points, 3)

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
                if grid[neighbor[0]][neighbor[1]] != VAL_FREE:
                    continue
            else:
                continue
            tentative_g_score = g_score[current] + 1
            if neighbor in close_set and tentative_g_score >= g_score.get(neighbor, 0):
                continue
            if tentative_g_score < g_score.get(neighbor, float('inf')) or neighbor not in [i[1] for i in oheap]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (f_score[neighbor], neighbor))
    return []

# --- MATRİS KAYDETME ---
def save_map_matrix(grid, filename="harita_matrisi.txt"):
    """
    Haritayı 2 (Bilinmeyen), 1 (Boş), 0 (Duvar) kodlarıyla kaydeder.
    """
    rows = len(grid[0])
    cols = len(grid)
    
    try:
        with open(filename, "w") as f:
            for y in range(rows):
                line = []
                for x in range(cols):
                    val = int(grid[x][y])
                    line.append(str(val))
                f.write(" ".join(line) + "\n")
        print(f"Harita başarıyla kaydedildi: {filename}")
    except Exception as e:
        print(f"Kaydetme hatası: {e}")

def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Robot Haritalama - Otomatik Durdurma")
    clock = pygame.time.Clock()
    
    font_large = pygame.font.SysFont("Arial", 30, bold=True)
    font_small = pygame.font.SysFont("Arial", 18, bold=True)

    # Harita
    real_world_map = np.ones((COLS, ROWS), dtype=int) * VAL_FREE 
    real_world_map[10:15, 10:20] = VAL_WALL
    real_world_map[25:30, 5:15] = VAL_WALL
    real_world_map[5:35, 25:26] = VAL_WALL
    real_world_map[2:5, 2:5] = VAL_WALL 

    # Robotun Hafızası
    known_map = np.full((COLS, ROWS), VAL_UNKNOWN, dtype=int)

    robot = Robot(50, 50)

    running = True
    while running:
        clock.tick(60)
        
        # --- OLAYLARI DİNLE ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    if robot.mode == "EXPLORE":
                        robot.mode = "WAITING"
                    elif robot.mode == "WAITING":
                        robot.mode = "EXPLORE" 
                
                if event.key == pygame.K_s:
                    save_map_matrix(known_map, "harita_matrisi.txt")

            if robot.mode == "WAITING" and event.type == pygame.MOUSEBUTTONDOWN:
                m_x, m_y = pygame.mouse.get_pos()
                target_grid = (m_x // GRID_SIZE, m_y // GRID_SIZE)
                start_grid = (int(robot.x) // GRID_SIZE, int(robot.y) // GRID_SIZE)
                
                if known_map[target_grid[0]][target_grid[1]] == VAL_FREE:
                    path = a_star_search(known_map, start_grid, target_grid)
                    if path:
                        robot.path = path
                        robot.mode = "NAVIGATE"
                    else:
                        print("Yol bulunamadı.")

        # --- DURUM MAKİNESİ VE OTOMATİK DURDURMA ---
        if robot.mode == "EXPLORE":
            robot.auto_explore(real_world_map)
            
            # --- YENİ EKLENEN KISIM: Keşif Oranı Hesabı ---
            total_cells = COLS * ROWS
            # Bilinmeyen (2) olmayan hücreler, keşfedilmiş demektir (1 veya 0)
            unknown_count = np.count_nonzero(known_map == VAL_UNKNOWN)
            explored_ratio = 1.0 - (unknown_count / total_cells)
            
            # Eğer keşif oranı hedefe ulaştıysa dur
            if explored_ratio >= EXPLORATION_GOAL:
                robot.mode = "WAITING"
                print(f"Haritanın %{int(explored_ratio*100)}'si tarandı. Keşif tamamlandı.")
                save_map_matrix(known_map, "otomatik_harita_tamamlandi.txt")
        
        elif robot.mode == "NAVIGATE":
            robot.navigate()

        # --- SENSÖR ---
        r_grid_x = int(robot.x) // GRID_SIZE
        r_grid_y = int(robot.y) // GRID_SIZE
        view_range = 5 
        for i in range(-view_range, view_range + 1):
            for j in range(-view_range, view_range + 1):
                nx, ny = r_grid_x + i, r_grid_y + j
                if 0 <= nx < COLS and 0 <= ny < ROWS:
                    known_map[nx][ny] = real_world_map[nx][ny]

        # --- ÇİZİM ---
        win.fill((0, 0, 0))
        for x in range(COLS):
            for y in range(ROWS):
                rect = (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                cell_val = known_map[x][y]
                if cell_val == VAL_UNKNOWN: # 2
                    pygame.draw.rect(win, UNKNOWN_COLOR, rect)
                elif cell_val == VAL_FREE: # 1
                    pygame.draw.rect(win, FREE_COLOR, rect)
                    pygame.draw.rect(win, (255,255,255), rect, 1)
                elif cell_val == VAL_WALL: # 0
                    pygame.draw.rect(win, WALL_COLOR, rect)

        robot.draw(win)
        
        # --- BİLGİ YAZILARI ---
        if robot.mode == "EXPLORE":
            # İlerleme durumunu göster
            progress = int((1.0 - (np.count_nonzero(known_map == VAL_UNKNOWN) / (COLS*ROWS))) * 100)
            text_surf = font_small.render(f"Keşfediliyor... %{progress} (Hedef: %{int(EXPLORATION_GOAL*100)})", True, INFO_COLOR)
            win.blit(text_surf, (10, 10))
            
        elif robot.mode == "WAITING":
            text_surf = font_large.render("KEŞİF TAMAMLANDI - HEDEF SEÇİN", True, TEXT_COLOR)
            text_rect = text_surf.get_rect(center=(WIDTH/2, HEIGHT/2))
            pygame.draw.rect(win, (255, 255, 255), text_rect.inflate(20, 20))
            win.blit(text_surf, text_rect)
            
            sub_text = font_small.render("'Q': Tekrar Gez | 'S': Kaydet", True, INFO_COLOR)
            win.blit(sub_text, (10, HEIGHT - 30))

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
