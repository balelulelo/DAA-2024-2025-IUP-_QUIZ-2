import pygame
import random
import collections
import sys
import math
import os

# Constants 
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CELL_SIZE = 30
MAZE_WIDTH = SCREEN_WIDTH // CELL_SIZE
MAZE_HEIGHT = SCREEN_HEIGHT // CELL_SIZE
EXTRA_WALL_REMOVAL_PERCENT = 0.15

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)
WARNING_YELLOW = (255, 255, 100) 

# Movement
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

# Enemy AI
ENEMY_DETECTION_RADIUS = 10
ENEMY_CHASE_SPEED = 300
ENEMY_PATROL_SPEED = 500

# Cell Class
class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'N': True, 'S': True, 'E': True, 'W': True}
        self.visited = False

# Maze Class
class Maze:
    def __init__(self, width, height):
        self.width = width; self.height = height
        self.grid = [[Cell(x, y) for x in range(width)] for y in range(height)]
        self._generate_maze(); self._remove_extra_walls()
        self.exit_pos = (width - 1, height - 1)
    def _get_neighbors(self, cell):
        neighbors = []; x, y = cell.x, cell.y
        if x > 0 and not self.grid[y][x - 1].visited: neighbors.append(self.grid[y][x - 1])
        if x < self.width - 1 and not self.grid[y][x + 1].visited: neighbors.append(self.grid[y][x + 1])
        if y > 0 and not self.grid[y - 1][x].visited: neighbors.append(self.grid[y - 1][x])
        if y < self.height - 1 and not self.grid[y + 1][x].visited: neighbors.append(self.grid[y + 1][x])
        return neighbors
    def _remove_walls(self, current, next_cell):
        dx = current.x - next_cell.x; dy = current.y - next_cell.y
        if dx == 1: current.walls['W'], next_cell.walls['E'] = False, False
        elif dx == -1: current.walls['E'], next_cell.walls['W'] = False, False
        elif dy == 1: current.walls['N'], next_cell.walls['S'] = False, False
        elif dy == -1: current.walls['S'], next_cell.walls['N'] = False, False
    def _generate_maze(self):
        stack = []; start_cell = self.grid[0][0]; start_cell.visited = True; stack.append(start_cell)
        while stack:
            current_cell = stack[-1]; neighbors = self._get_neighbors(current_cell)
            if neighbors: next_cell = random.choice(neighbors); next_cell.visited = True; self._remove_walls(current_cell, next_cell); stack.append(next_cell)
            else: stack.pop()
        for row in self.grid:
            for cell_obj in row: cell_obj.visited = False
    def _remove_extra_walls(self):
        num_walls_to_remove = int(self.width * self.height * EXTRA_WALL_REMOVAL_PERCENT)
        removed_count = 0
        while removed_count < num_walls_to_remove:
            x = random.randint(0, self.width - 2); y = random.randint(0, self.height - 2)
            current_cell = self.grid[y][x]; wall_dir = random.choice(['E', 'S'])
            if wall_dir == 'E' and current_cell.walls['E']: self._remove_walls(current_cell, self.grid[y][x+1]); removed_count += 1
            elif wall_dir == 'S' and current_cell.walls['S']: self._remove_walls(current_cell, self.grid[y+1][x]); removed_count += 1
    def _get_wall_dir(self, direction):
        if direction == UP: return 'N'
        elif direction == DOWN: return 'S'
        elif direction == LEFT: return 'W'
        elif direction == RIGHT: return 'E'
        return None
    def can_move(self, x, y, direction):
        if not (0 <= x < self.width and 0 <= y < self.height): return False
        cell = self.grid[y][x]
        wall_to_check = self._get_wall_dir(direction)
        if wall_to_check is None: return False
        return not cell.walls[wall_to_check]
    def get_valid_neighbors_for_pathfinding(self, x, y):
        neighbors = []
        for d in DIRECTIONS:
            if self.can_move(x, y, d):
                neighbors.append((x + d[0], y + d[1]))
        return neighbors
    def draw(self, screen):
        screen.fill(BLACK)
        for y_coord in range(self.height):
            for x_coord in range(self.width):
                px, py = x_coord * CELL_SIZE, y_coord * CELL_SIZE
                cell = self.grid[y_coord][x_coord]
                wall_color = WHITE
                if cell.walls['N']: pygame.draw.line(screen, wall_color, (px, py), (px + CELL_SIZE, py))
                if cell.walls['S']: pygame.draw.line(screen, wall_color, (px, py + CELL_SIZE), (px + CELL_SIZE, py + CELL_SIZE))
                if cell.walls['E']: pygame.draw.line(screen, wall_color, (px + CELL_SIZE, py), (px + CELL_SIZE, py + CELL_SIZE))
                if cell.walls['W']: pygame.draw.line(screen, wall_color, (px, py), (px, py + CELL_SIZE))
        ex, ey = self.exit_pos
        pygame.draw.rect(screen, GOLD, (ex * CELL_SIZE + 2, ey * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4))

# BFS Function 
def bfs(maze, start_pos, end_pos):
    queue = collections.deque([[start_pos]]); visited = {start_pos}
    while queue:
        path = queue.popleft(); x, y = path[-1]
        if (x, y) == end_pos: return path
        for next_x, next_y in maze.get_valid_neighbors_for_pathfinding(x, y):
            if (next_x, next_y) not in visited:
                visited.add((next_x, next_y)); new_path = list(path); new_path.append((next_x, next_y)); queue.append(new_path)
    return None

# Player Class 
class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y; self.radius = CELL_SIZE // 3
    def move(self, dx, dy, maze):
        direction = (dx, dy)
        if maze.can_move(self.x, self.y, direction): self.x += dx; self.y += dy
    def draw(self, screen):
        px = self.x * CELL_SIZE + CELL_SIZE // 2; py = self.y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, GREEN, (px, py), self.radius)

# Enemy Class 
class Enemy:
    def __init__(self, x, y):
        self.x, self.y = x, y; self.radius = CELL_SIZE // 3; self.path = []
        self.state = 'PATROL'; self.last_known_pos = None; self.detection_radius = ENEMY_DETECTION_RADIUS
        self.move_delay = ENEMY_PATROL_SPEED; self.last_move_time = pygame.time.get_ticks()
        self.bfs_delay = 500; self.last_bfs_time = 0; self.patrol_target = None
    def update_ai(self, maze, player_pos):
        current_time = pygame.time.get_ticks(); dist_to_player = math.hypot(self.x - player_pos[0], self.y - player_pos[1])
        if dist_to_player <= self.detection_radius:
            if self.state != 'CHASING': self.path = []
            self.state = 'CHASING'; self.last_known_pos = player_pos; self.move_delay = ENEMY_CHASE_SPEED
        elif self.state == 'CHASING': self.state = 'TO_LAST_KNOWN'; self.path = []
        elif self.state == 'TO_LAST_KNOWN' and ((self.x, self.y) == self.last_known_pos or self.last_known_pos is None):
            self.state = 'PATROL'; self.last_known_pos = None; self.path = []; self.move_delay = ENEMY_PATROL_SPEED
        needs_new_path = not self.path
        if self.state == 'CHASING':
            if (needs_new_path or (current_time - self.last_bfs_time > self.bfs_delay)) and self.last_known_pos:
                self.path = bfs(maze, (self.x, self.y), self.last_known_pos); self.last_bfs_time = current_time
        elif self.state == 'TO_LAST_KNOWN':
             if needs_new_path and self.last_known_pos: self.path = bfs(maze, (self.x, self.y), self.last_known_pos)
        elif self.state == 'PATROL':
            if needs_new_path:
                target_x = random.randint(0, maze.width - 1); target_y = random.randint(0, maze.height - 1)
                self.patrol_target = (target_x, target_y)
                self.path = bfs(maze, (self.x, self.y), self.patrol_target)
                if not self.path: self.patrol_target = None
    def move(self, maze):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time > self.move_delay:
            if self.path and len(self.path) > 1: self.x, self.y = self.path[1]; self.path.pop(0)
            else: self.path = []
            self.last_move_time = current_time
    def draw(self, screen):
        px = self.x * CELL_SIZE + CELL_SIZE // 2; py = self.y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, RED, (px, py), self.radius)

# Game Class 
class Game:
    def __init__(self):
        pygame.mixer.init()
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Im About to Run: 2D Maze")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 30)
        self.warning_font = pygame.font.Font(None, 60)

        # Load Assets 
        self.jumpscare_sound = None
        self.win_sound = None 
        jumpscare_sound_path = 'assets/lose.wav'
        win_sound_path = 'assets/win.wav'
        background_music_path = 'assets/bgm.mp3'
        try:
            if os.path.exists(jumpscare_sound_path): self.jumpscare_sound = pygame.mixer.Sound(jumpscare_sound_path)
            else: print(f"Warning: Lose sound ('{jumpscare_sound_path}') not found.")
        except Exception as e: print(f"Error loading lose sound: {e}")
        try:
            if os.path.exists(win_sound_path): self.win_sound = pygame.mixer.Sound(win_sound_path)
            elif os.path.exists('win_sound.ogg'): self.win_sound = pygame.mixer.Sound('win_sound.ogg')
            else: print(f"Warning: Win sound ('{win_sound_path}' or .ogg) not found.")
        except Exception as e: print(f"Error loading win sound: {e}")
        try:
            if os.path.exists(background_music_path): pygame.mixer.music.load(background_music_path); pygame.mixer.music.set_volume(0.4)
            elif os.path.exists('background_music.ogg'): pygame.mixer.music.load('background_music.ogg'); pygame.mixer.music.set_volume(0.4)
            else: print(f"Warning: Background music ('{background_music_path}' or .ogg) not found.")
        except Exception as e: print(f"Error loading music: {e}")

        self.reset_game(initial_start=True) # <-- Warning screen

    def _scale_image(self, image):
        img_w, img_h = image.get_size()
        if img_w > 0 and img_h > 0:
            scale = min(SCREEN_WIDTH * 0.8 / img_w, SCREEN_HEIGHT * 0.8 / img_h)
            new_w, new_h = int(img_w * scale), int(img_h * scale)
            return pygame.transform.scale(image, (new_w, new_h))
        return None

    def reset_game(self, initial_start=False): 
        self.maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
        self.player = Player(0, 0)
        self.enemy = Enemy(MAZE_WIDTH - 1, 0)
        self.lose_sound_played = False
        self.win_sound_played = False
        pygame.mixer.music.stop()
       
        self.game_state = "warning"


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()

            if self.game_state == "warning":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.game_state = "playing"
                        try: pygame.mixer.music.play(-1) 
                        except pygame.error: print("Could not play background music.")
                    elif event.key == pygame.K_r: 
                        self.reset_game()

            elif self.game_state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP: self.player.move(0, -1, self.maze)
                    elif event.key == pygame.K_DOWN: self.player.move(0, 1, self.maze)
                    elif event.key == pygame.K_LEFT: self.player.move(-1, 0, self.maze)
                    elif event.key == pygame.K_RIGHT: self.player.move(1, 0, self.maze)
                    elif event.key == pygame.K_r:
                        self.reset_game()

            elif self.game_state in ["win", "lose"]: 
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.reset_game()

    def update(self):
        if self.game_state == "playing":
            self.enemy.update_ai(self.maze, (self.player.x, self.player.y))
            self.enemy.move(self.maze)
            if (self.player.x, self.player.y) == self.maze.exit_pos:
                self.game_state = "win"; pygame.mixer.music.stop()
                if not self.win_sound_played and self.win_sound: self.win_sound.play(); self.win_sound_played = True
            if (self.player.x, self.player.y) == (self.enemy.x, self.enemy.y):
                self.game_state = "lose"; pygame.mixer.music.stop()
                if not self.lose_sound_played and self.jumpscare_sound: self.jumpscare_sound.play(); self.lose_sound_played = True

    def draw_message(self, message, color, on_image=False):
        if on_image:
            text2 = self.font.render("Press 'R' to Restart", True, WHITE)
            text_rect2 = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            self.screen.blit(text2, text_rect2)
        else:
            text = self.font.render(message, True, color); text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)); self.screen.blit(text, text_rect)
            text2 = self.font.render("Press 'R' to Restart", True, WHITE); text_rect2 = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)); self.screen.blit(text2, text_rect2)

    def draw_hud(self):
        enemy_text = self.small_font.render(f"Enemy: {self.enemy.state}", True, RED)
        self.screen.blit(enemy_text, (10, 10))

    def draw_warning_screen(self):
        self.screen.fill(BLACK)
        
        title_text = self.warning_font.render("WARNING!", True, RED)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 - 30))
        self.screen.blit(title_text, title_rect)

        warn_text = self.font.render("This game contains loud sounds.", True, WARNING_YELLOW)
        warn_rect = warn_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(warn_text, warn_rect)

        start_text = self.font.render("Press SPACE to Start", True, WHITE)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3 + 30))
        self.screen.blit(start_text, start_rect)

    def draw(self):
        if self.game_state == "warning": 
            self.draw_warning_screen()

        elif self.game_state == "lose" and self.jumpscare_image:
            self.screen.fill(BLACK)
            img_rect = self.jumpscare_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(self.jumpscare_image, img_rect)
            self.draw_message("", RED, on_image=True)

        elif self.game_state == "win" and self.win_image:
            self.screen.fill(BLACK)
            img_rect = self.win_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(self.win_image, img_rect)
            self.draw_message("", GREEN, on_image=True)

        elif self.game_state == "playing": 
            self.maze.draw(self.screen)
            self.player.draw(self.screen)
            self.enemy.draw(self.screen)
            self.draw_hud()

        elif self.game_state == "win":
             self.maze.draw(self.screen)
             self.player.draw(self.screen)
             self.draw_message("You Escaped!", GREEN)

        elif self.game_state == "lose":
             self.maze.draw(self.screen)
             self.player.draw(self.screen)
             self.enemy.draw(self.screen)
             self.draw_message("You Were Caught!", RED)

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events(); self.update(); self.draw(); self.clock.tick(30)

# Main Execution
if __name__ == "__main__":
    game = Game()
    game.run()
