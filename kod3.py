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

# Hedef Keşif Oranı (%96 taranınca işlem biter)
EXPLORATION_GOAL = 0.96

# Renkler
UNKNOWN_COLOR = (240, 230, 140) 
FREE_COLOR = (200, 200, 200)    
WALL_COLOR = (0, 0, 0)          
ROBOT_COLOR = (255, 0, 0)       
PATH_COLOR = (0, 0, 255)        
TEXT_COLOR = (0, 0, 0)       
INFO_COLOR = (0, 0, 150)      

# Durum Kodları
VAL_UNKNOWN = 2
VAL_FREE = 1
VAL_WALL = 0

class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = 8 
        self.path = []
        self.mode = "EXPLORE" # Modlar: EXPLORE, PAUSED, NAVIGATE, FINISHED

    def auto_explore(self, grid):
        """Kusurlu Sekme Mantığı"""
        dx = math.cos(self.angle) * self.speed
        dy = math.sin(self.angle) * self.speed

        next_x = self.x + dx
        next_y = self.y + dy

        next_grid_x = int(np.clip(next_x // GRID_SIZE, 0, COLS - 1))
        next_grid_y = int(np.clip(next_y // GRID_SIZE, 0, ROWS - 1))
        curr_grid_y = int(np.clip(self.y // GRID_SIZE, 0, ROWS - 1))

        hit = False

        # Sınır Kontrolü
        if next_x - ROBOT_RADIUS < 0 or next_x + ROBOT_RADIUS > WIDTH:
            dx = -dx
            hit = True
        if next_y - ROBOT_RADIUS < 0 or next_y + ROBOT_RADIUS > HEIGHT:
            dy = -dy
            hit = True

        # Duvar Kontrolü
        if not hit:
            if grid[next_grid_x][next_grid_y] == VAL_WALL:
                hit = True
                check_x = int((self.x + dx) // GRID_SIZE)
                if 0 <= check_x < COLS and grid[check_x][curr_grid_y] == VAL_WALL:
                    dx = -dx
                else:
                    dy = -dy 

        # Yön Değiştirme
        if hit:
            base_angle = math.atan2(dy, dx)
            noise = random.uniform(-0.7, 0.7) 
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
                    # Hedefe varınca, eğer tarama bitmişse FINISHED moduna,
                    # yoksa PAUSED moduna dönsün.
                    if self.mode != "FINISHED":
                        self.mode = "PAUSED"
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

def save_map_matrix(grid, filename):
    rows = len(grid[0])
    cols = len(grid)
    try:
        with open(filename, "w") as f:
            for y in range(rows):
                line = []
                for x in range(cols):
                    line.append(str(int(grid[x][y])))
                f.write(" ".join(line) + "\n")
        print(f"Harita başarıyla kaydedildi: {filename}")
    except Exception as e:
        print(f"Kaydetme hatası: {e}")

def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Robot Haritalama")
    clock = pygame.time.Clock()
    
    font = pygame.font.SysFont("Arial", 20, bold=True)
    font_msg = pygame.font.SysFont("Arial", 32, bold=True)

    # Harita
    real_world_map = np.ones((COLS, ROWS), dtype=int) * VAL_FREE 
    real_world_map[10:15, 10:20] = VAL_WALL
    real_world_map[25:30, 5:15] = VAL_WALL
    real_world_map[5:35, 25:26] = VAL_WALL
    real_world_map[2:5, 2:5] = VAL_WALL 

    # Robotun Hafızası
    known_map = np.full((COLS, ROWS), VAL_UNKNOWN, dtype=int)
    robot = Robot(50, 50)
    
    map_version = 1

    running = True
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                # Q: Durdur / Devam Et
                if event.key == pygame.K_q:
                    if robot.mode == "EXPLORE": 
                        robot.mode = "PAUSED"
                    elif robot.mode == "PAUSED": 
                        robot.mode = "EXPLORE"
                
                # S: Kaydet
                if event.key == pygame.K_s:
                    save_map_matrix(known_map, f"manuel_kayit_{map_version}.txt")
                    map_version += 1

            # Fare Navigasyonu (Duraklatıldığında veya Bittiğinde çalışır)
            if (robot.mode == "PAUSED" or robot.mode == "FINISHED") and event.type == pygame.MOUSEBUTTONDOWN:
                m_x, m_y = pygame.mouse.get_pos()
                target_grid = (m_x // GRID_SIZE, m_y // GRID_SIZE)
                start_grid = (int(robot.x) // GRID_SIZE, int(robot.y) // GRID_SIZE)
                if known_map[target_grid[0]][target_grid[1]] == VAL_FREE:
                    path = a_star_search(known_map, start_grid, target_grid)
                    if path:
                        robot.path = path
                        # Eğer bitmişse FINISHED modunda kalsın ama hareket etsin diye özel bir durum yaratmıyoruz,
                        # sadece path bitene kadar navigate fonksiyonu çalışacak.
                        # Ancak hareket fonksiyonumuz moda bağlı olduğu için geçici olarak NAVIGATE yapıyoruz.
                        robot.mode = "NAVIGATE"

        # --- LOJİK ---
        if robot.mode == "EXPLORE":
            robot.auto_explore(real_world_map)
            
            # Yüzde Hesabı
            total_cells = COLS * ROWS
            unknown_count = np.count_nonzero(known_map == VAL_UNKNOWN)
            explored_ratio = 1.0 - (unknown_count / total_cells)
            
            # HEDEFE ULAŞINCA OTOMATİK DUR VE KAYDET
            if explored_ratio >= EXPLORATION_GOAL:
                print("Tarama bitti. Harita kaydediliyor.")
                save_map_matrix(known_map, "tamamlanmis_harita.txt")
                robot.mode = "FINISHED"
        
        elif robot.mode == "NAVIGATE":
            robot.navigate()
            # Yol bitince, eğer harita zaten bitmişse FINISHED moduna dön
            if not robot.path:
                total_cells = COLS * ROWS
                unknown_count = np.count_nonzero(known_map == VAL_UNKNOWN)
                if (1.0 - unknown_count / total_cells) >= EXPLORATION_GOAL:
                    robot.mode = "FINISHED"
                else:
                    robot.mode = "PAUSED"

        # Sensör Güncelleme
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
                if cell_val == VAL_UNKNOWN:
                    pygame.draw.rect(win, UNKNOWN_COLOR, rect)
                elif cell_val == VAL_FREE:
                    pygame.draw.rect(win, FREE_COLOR, rect)
                    pygame.draw.rect(win, (255,255,255), rect, 1)
                elif cell_val == VAL_WALL:
                    pygame.draw.rect(win, WALL_COLOR, rect)

        robot.draw(win)

        # --- ARAYÜZ ---
        # Sol üst bilgi
        info_bg = pygame.Rect(5, 5, 360, 30)
        pygame.draw.rect(win, (255, 255, 255), info_bg)
        pygame.draw.rect(win, (0, 0, 0), info_bg, 2)
        
        # 'R' tuşunu kaldırdık
        keys_text = "Tuşlar ->  S: Kaydet  |  Q: Durdur/Devam"
        text_surf = font.render(keys_text, True, TEXT_COLOR)
        win.blit(text_surf, (15, 10))

        # BİTİŞ MESAJI
        if robot.mode == "FINISHED":
            msg_bg = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 50, 400, 100)
            pygame.draw.rect(win, (255, 255, 255), msg_bg)
            pygame.draw.rect(win, (0, 0, 0), msg_bg, 3)
            
            msg1 = font_msg.render("TARAMA TAMAMLANDI!", True, (0, 150, 0))
            msg2 = font.render("Gitmek için haritaya tıklayabilirsiniz.", True, (0, 0, 0))
            
            win.blit(msg1, (WIDTH//2 - msg1.get_width()//2, HEIGHT//2 - 30))
            win.blit(msg2, (WIDTH//2 - msg2.get_width()//2, HEIGHT//2 + 10))

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
