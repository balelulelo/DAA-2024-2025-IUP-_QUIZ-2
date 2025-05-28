import pygame
import random
import sys
import math 

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
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)
RED = (255, 0, 0)

# Movement
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

# Enemy AI 
ENEMY_PATROL_SPEED = 600

# Cell Class
class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y; self.walls = {'N': True, 'S': True, 'E': True, 'W': True}; self.visited = False

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
            for cell in row: cell.visited = False

    def _remove_extra_walls(self):
        num_walls_to_remove = int(self.width * self.height * EXTRA_WALL_REMOVAL_PERCENT)
        removed_count = 0
        while removed_count < num_walls_to_remove:
            x = random.randint(0, self.width - 2); y = random.randint(0, self.height - 2)
            cell = self.grid[y][x]; wall_dir = random.choice(['E', 'S'])
            if wall_dir == 'E' and cell.walls['E']: self._remove_walls(cell, self.grid[y][x+1]); removed_count += 1
            elif wall_dir == 'S' and cell.walls['S']: self._remove_walls(cell, self.grid[y+1][x]); removed_count += 1

    def _get_wall_dir(self, direction): 
        if direction == UP: return 'N'
        elif direction == DOWN: return 'S'
        elif direction == LEFT: return 'W'
        elif direction == RIGHT: return 'E'
        return None

    def can_move(self, x, y, direction): 
        if not (0 <= x < self.width and 0 <= y < self.height): return False
        cell = self.grid[y][x]; wall_to_check = self._get_wall_dir(direction)
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
        for y in range(self.height):
            for x in range(self.width):
                px, py = x * CELL_SIZE, y * CELL_SIZE; cell = self.grid[y][x]
                if cell.walls['N']: pygame.draw.line(screen, WHITE, (px, py), (px + CELL_SIZE, py))
                if cell.walls['S']: pygame.draw.line(screen, WHITE, (px, py + CELL_SIZE), (px + CELL_SIZE, py + CELL_SIZE))
                if cell.walls['E']: pygame.draw.line(screen, WHITE, (px + CELL_SIZE, py), (px + CELL_SIZE, py + CELL_SIZE))
                if cell.walls['W']: pygame.draw.line(screen, WHITE, (px, py), (px, py + CELL_SIZE))
        ex, ey = self.exit_pos
        pygame.draw.rect(screen, GOLD, (ex * CELL_SIZE + 2, ey * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4))


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
        self.x, self.y = x, y
        self.radius = CELL_SIZE // 3
        self.move_delay = ENEMY_PATROL_SPEED
        self.last_move_time = pygame.time.get_ticks()

    def move(self, maze):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time > self.move_delay:
            valid_moves = maze.get_valid_neighbors_for_pathfinding(self.x, self.y)
            if valid_moves:
                self.x, self.y = random.choice(valid_moves)
            self.last_move_time = current_time

    def draw(self, screen):
        px = self.x * CELL_SIZE + CELL_SIZE // 2
        py = self.y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, RED, (px, py), self.radius)

# Game Class
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Quiz 2")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 50)
        self.reset_game()

    def reset_game(self):
        self.maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
        self.player = Player(0, 0)
        self.enemy = Enemy(MAZE_WIDTH - 1, 0)
        self.game_state = "playing"

    def handle_events(self): 
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if self.game_state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP: self.player.move(0, -1, self.maze)
                    elif event.key == pygame.K_DOWN: self.player.move(0, 1, self.maze)
                    elif event.key == pygame.K_LEFT: self.player.move(-1, 0, self.maze)
                    elif event.key == pygame.K_RIGHT: self.player.move(1, 0, self.maze)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.reset_game()

    def update(self):
        if self.game_state == "playing":
            self.enemy.move(self.maze) 
            if (self.player.x, self.player.y) == self.maze.exit_pos:
                self.game_state = "win"

    def draw_message(self, message, color):
        text = self.font.render(message, True, color); text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)); self.screen.blit(text, text_rect)
        text2 = self.font.render("Press 'R' to Restart", True, WHITE); text_rect2 = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)); self.screen.blit(text2, text_rect2)

    def draw(self):
        self.maze.draw(self.screen)
        self.player.draw(self.screen)
        self.enemy.draw(self.screen) 

        if self.game_state == "win":
            self.draw_message("You Escaped!", GREEN)

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(30)

# Main Execution 
if __name__ == "__main__":
    game = Game()
    game.run()
