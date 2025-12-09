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

# Renkler
UNKNOWN_COLOR = (240, 230, 140) 
FREE_COLOR = (200, 200, 200)    
WALL_COLOR = (0, 0, 0)          
ROBOT_COLOR = (255, 0, 0)       
PATH_COLOR = (0, 0, 255)        
TEXT_COLOR = (0, 100, 0)        

# Durum Kodları
VAL_UNKNOWN = 2
VAL_FREE = 1
VAL_WALL = 0

class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = 8 # Hızı biraz daha artırdım, daha çabuk bitirsin diye
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
                # Yan duvara mı çarptı?
                if 0 <= check_x < COLS and grid[check_x][curr_grid_y] == VAL_WALL:
                    dx = -dx
                else:
                    dy = -dy 

        # --- GÜNCELLENMİŞ KISIM: AÇIYA DAHA FAZLA RASTGELELİK EKLEME ---
        if hit:
            base_angle = math.atan2(dy, dx)
            
            # ESKİSİ: random.uniform(-0.35, 0.35) -> Yaklaşık 20 derece
            # YENİSİ: random.uniform(-0.7, 0.7) -> Yaklaşık 40 derece sapma
            # Bu, robotun kısır döngüye girme ihtimalini ciddi oranda azaltır.
            noise = random.uniform(-0.7, 0.7) 
            self.angle = base_angle + noise
        else:
            self.angle = math.atan2(dy, dx)

        # Hareketi Uygula
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # Sınırların içinde kal
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
                    print("Hedefe ulaşıldı.")
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

# --- YENİ EKLENEN FONKSİYON: MATRİS KAYDETME ---
def save_map_matrix(grid, filename="otomatik_harita.txt"):
    """Haritayı metin dosyası olarak kaydeder"""
    cols = len(grid)
    rows = len(grid[0])
    
    try:
        with open(filename, "w") as f:
            # Görsel olarak doğru olması için satır satır (y) okuyup yazıyoruz
            for y in range(rows):
                line = []
                for x in range(cols):
                    line.append(str(int(grid[x][y])))
                f.write(" ".join(line) + "\n")
        print(f"Harita matrisi başarıyla kaydedildi: {filename}")
    except Exception as e:
        print(f"Dosya kaydedilirken hata oluştu: {e}")

# A* ve Yardımcı Fonksiyonlar
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

def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Seken Robot Simülasyonu")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 30, bold=True)

    # Harita
    real_world_map = np.ones((COLS, ROWS), dtype=int) * VAL_FREE 
    # Duvarlar
    real_world_map[10:15, 10:20] = VAL_WALL
    real_world_map[25:30, 5:15] = VAL_WALL
    real_world_map[5:35, 25:26] = VAL_WALL
    real_world_map[2:5, 2:5] = VAL_WALL
    real_world_map[35:38, 3:6] = VAL_WALL

    known_map = np.full((COLS, ROWS), VAL_UNKNOWN, dtype=int)

    robot = Robot(50, 50)
    
    # %100 Keşif (Not: Rastgele hareketle %100 yapmak bazen çok uzun sürer, 
    # bu yüzden robot inatçı bir şekilde sekecektir)
    EXPLORATION_GOAL = 0.99 + 0.01

    running = True
    while running:
        clock.tick(60) # 60 FPS
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if robot.mode == "WAITING" and event.type == pygame.MOUSEBUTTONDOWN:
                m_x, m_y = pygame.mouse.get_pos()
                target_grid = (m_x // GRID_SIZE, m_y // GRID_SIZE)
                start_grid = (int(robot.x) // GRID_SIZE, int(robot.y) // GRID_SIZE)
                
                if known_map[target_grid[0]][target_grid[1]] == VAL_FREE:
                    path = a_star_search(known_map, start_grid, target_grid)
                    if path:
                        robot.path = path
                        robot.mode = "NAVIGATE"

        # --- DURUM MAKİNESİ ---
        if robot.mode == "EXPLORE":
            robot.auto_explore(real_world_map)
            
            unknown_cells = np.count_nonzero(known_map == VAL_UNKNOWN)
            explored_ratio = 1 - (unknown_cells / (COLS * ROWS))
            
            # GÜNCELLENMİŞ KISIM: Hedefe ulaşınca OTOMATİK KAYIT
            if explored_ratio >= EXPLORATION_GOAL:
                print("Hedef orana ulaşıldı. Harita kaydediliyor...")
                save_map_matrix(known_map, "otomatik_harita.txt")
                robot.mode = "WAITING"
        
        elif robot.mode == "NAVIGATE":
            robot.navigate()
            if not robot.path:
                robot.mode = "WAITING"

        # --- SENSÖR ---
        r_grid_x = int(robot.x) // GRID_SIZE
        r_grid_y = int(robot.y) // GRID_SIZE
        view_range = 4
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
                if cell_val == VAL_UNKNOWN:
                    pygame.draw.rect(win, UNKNOWN_COLOR, rect)
                elif cell_val == VAL_FREE:
                    pygame.draw.rect(win, FREE_COLOR, rect)
                    pygame.draw.rect(win, (255,255,255), rect, 1)
                elif cell_val == VAL_WALL:
                    pygame.draw.rect(win, WALL_COLOR, rect)

        robot.draw(win)
        
        if robot.mode == "WAITING":
            text_surf = font.render("KEŞİF BİTTİ - HARİTA KAYDEDİLDİ", True, TEXT_COLOR)
            text_rect = text_surf.get_rect(center=(WIDTH/2, HEIGHT/2))
            pygame.draw.rect(win, (255, 255, 255), text_rect.inflate(20, 20))
            win.blit(text_surf, text_rect)
            
            # Alt bilgi
            sub_text = font.render("Gitmek için bir yere tıklayın", True, (0,0,0))
            # Font boyutu için basit bir scale işlemi veya yeni font tanımlanabilir, 
            # şimdilik aynı fontla altına yazdıralım.
            win.blit(sub_text, (WIDTH/2 - 150, HEIGHT/2 + 40))

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()