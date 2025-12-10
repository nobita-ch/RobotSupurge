import pygame
import math
import numpy as np
import heapq

# --- AYARLAR ---
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
COLS, ROWS = WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE
ROBOT_RADIUS = 10

# Renkler
UNKNOWN_COLOR = (240, 230, 140) # Sarı
FREE_COLOR = (200, 200, 200)    # Gri
WALL_COLOR = (0, 0, 0)          # Siyah
ROBOT_COLOR = (255, 0, 0)       # Kırmızı
PATH_COLOR = (0, 0, 255)        # Mavi
SENSOR_BOX_COLOR = (0, 255, 255)# Turkuaz
TEXT_COLOR = (0, 100, 0)        

# Durum Değerleri
VAL_UNKNOWN = 2
VAL_FREE = 1
VAL_WALL = 0

class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.path = []      
        self.target = None  
        self.finished = False
        self.paused = False # Duraklatma durumu
        
        # --- İSTEK: ÇAP 3 OLARAK REVİZE EDİLDİ ---
        # Merkezden 3 birim sağa/sola/yukarı/aşağı (Toplam genişlik 7 kare)
        self.view_range = 3 

    def sense(self, real_map, known_map):
        """Sensör: Etrafı tara ve hafızaya yaz"""
        r_grid_x = int(self.x // GRID_SIZE)
        r_grid_y = int(self.y // GRID_SIZE)
        
        for i in range(-self.view_range, self.view_range + 1):
            for j in range(-self.view_range, self.view_range + 1):
                nx, ny = r_grid_x + i, r_grid_y + j
                
                if 0 <= nx < COLS and 0 <= ny < ROWS:
                    known_map[nx][ny] = real_map[nx][ny]

    def think(self, known_map):
        """Rota Planlama"""
        if self.path or self.finished or self.paused:
            return 

        start_node = (int(self.x // GRID_SIZE), int(self.y // GRID_SIZE))
        
        # En yakın ulaşılabilir bilinmeyen alanı bul
        frontier_target = find_nearest_unknown(known_map, start_node)

        if frontier_target:
            self.path = a_star_search(known_map, start_node, frontier_target)
        else:
            # --- İSTEK: SİYAH BÖLGE İÇİNİ DÜZELTME ---
            # Eğer gidilecek ulaşılabilir sarı alan kalmadıysa, 
            # haritada kalan diğer tüm sarı alanlar (duvarların içi) 
            # ulaşılamaz demektir. Onları siyaha (Duvar) çeviriyoruz.
            self.finalize_map(known_map)
            
            print("Haritalama ve Temizlik Tamamlandı!")
            save_map_matrix(known_map, "final_harita.txt")
            self.finished = True

    def finalize_map(self, known_map):
        """
        Bitiş anında duvarların içinde kalan 'Bilinmeyen' (2) yerleri
        'Duvar' (0) olarak işaretler.
        """
        for x in range(COLS):
            for y in range(ROWS):
                if known_map[x][y] == VAL_UNKNOWN:
                    known_map[x][y] = VAL_WALL

    def move(self):
        """Hareket"""
        if self.paused or not self.path:
            return

        target_grid = self.path[0]
        target_px_x = target_grid[0] * GRID_SIZE + GRID_SIZE // 2
        target_px_y = target_grid[1] * GRID_SIZE + GRID_SIZE // 2

        dx = target_px_x - self.x
        dy = target_px_y - self.y
        dist = math.hypot(dx, dy)

        if dist < self.speed:
            self.x = target_px_x
            self.y = target_px_y
            self.path.pop(0) 
        else:
            angle = math.atan2(dy, dx)
            self.x += math.cos(angle) * self.speed
            self.y += math.sin(angle) * self.speed

    def draw(self, win):
        pygame.draw.circle(win, ROBOT_COLOR, (int(self.x), int(self.y)), ROBOT_RADIUS)
        
        # Sensör Alanı (Turkuaz Kare)
        top_left_grid_x = int(self.x // GRID_SIZE) - self.view_range
        top_left_grid_y = int(self.y // GRID_SIZE) - self.view_range
        px_x = top_left_grid_x * GRID_SIZE
        px_y = top_left_grid_y * GRID_SIZE
        size = (self.view_range * 2 + 1) * GRID_SIZE
        
        pygame.draw.rect(win, SENSOR_BOX_COLOR, (px_x, px_y, size, size), 2)

        if len(self.path) > 1:
            points = [(self.x, self.y)]
            for node in self.path:
                px = node[0] * GRID_SIZE + GRID_SIZE // 2
                py = node[1] * GRID_SIZE + GRID_SIZE // 2
                points.append((px, py))
            pygame.draw.lines(win, PATH_COLOR, False, points, 2)

# --- YARDIMCI ALGORİTMALAR ---

def find_nearest_unknown(grid, start):
    rows = len(grid[0])
    cols = len(grid)
    queue = [start]
    visited = set()
    visited.add(start)

    while queue:
        cx, cy = queue.pop(0)

        if grid[cx][cy] == VAL_UNKNOWN:
            return (cx, cy)

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cols and 0 <= ny < rows:
                if (nx, ny) not in visited:
                    # Sadece Duvar Olmayan yerlerden geçerek ara
                    if grid[nx][ny] != VAL_WALL:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
    return None

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
                if grid[neighbor[0]][neighbor[1]] == VAL_WALL:
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
                    val = int(grid[x][y])
                    line.append(str(val))
                f.write(" ".join(line) + "\n")
        print(f"-> Manuel Kayıt Yapıldı: {filename}")
    except Exception as e:
        print(f"HATA: {e}")

# --- ANA PROGRAM ---

def generate_map():
    grid = np.ones((COLS, ROWS), dtype=int) * VAL_FREE
    
    # Çerçeve
    grid[0:COLS, 0] = VAL_WALL
    grid[0:COLS, ROWS-1] = VAL_WALL
    grid[0, 0:ROWS] = VAL_WALL
    grid[COLS-1, 0:ROWS] = VAL_WALL
    
    # Büyük Bloklar (İçi dolu görünsün diye)
    grid[10:18, 10:25] = VAL_WALL 
    grid[30:35, 5:20] = VAL_WALL
    grid[5:35, 27:29] = VAL_WALL 
    
    return grid

def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Otonom Haritalama (Q: Durdur, S: Kaydet)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 20, bold=True)

    real_world_map = generate_map()
    known_map = np.full((COLS, ROWS), VAL_UNKNOWN, dtype=int)

    robot = Robot(50, 50) 

    running = True
    while running:
        clock.tick(60) 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # --- TUŞ KONTROLLERİ ---
            if event.type == pygame.KEYDOWN:
                # Q: Durdur / Devam (Haritayı kapatmaz)
                if event.key == pygame.K_q:
                    robot.paused = not robot.paused
                    status = "DURAKLATILDI" if robot.paused else "DEVAM EDİYOR"
                    print(f"Simülasyon {status}")

                # S: Manuel Kayıt (Haritayı kapatmaz)
                if event.key == pygame.K_s:
                    save_map_matrix(known_map, "manuel_kayit.txt")

        # --- ROBOT DÖNGÜSÜ ---
        # Sadece duraklatılmamışsa çalış
        if not robot.paused:
            robot.sense(real_world_map, known_map)
            robot.think(known_map)
            robot.move()

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
                    pygame.draw.rect(win, (255, 255, 255), rect, 1) 
                elif cell_val == VAL_WALL:
                    pygame.draw.rect(win, WALL_COLOR, rect)   

        robot.draw(win)

        # Bilgi Paneli
        info_rect = pygame.Rect(10, 10, 320, 40)
        pygame.draw.rect(win, (255, 255, 255), info_rect)
        pygame.draw.rect(win, (0, 0, 0), info_rect, 2)
        
        status_text = "DURAKLATILDI" if robot.paused else "ÇALIŞIYOR"
        if robot.finished: status_text = "TAMAMLANDI"
        
        info_msg = f"Durum: {status_text} | 'Q': Dur/Başla 'S': Kaydet"
        text_surf = font.render(info_msg, True, (0, 0, 0))
        win.blit(text_surf, (15, 20))

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()