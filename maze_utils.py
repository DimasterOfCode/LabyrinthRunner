import heapq
from constants import *


class MazeUtils:
    @staticmethod
    def check_collision(maze, x, y, radius):
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                cell_x = int((x + dx * radius) // CELL_SIZE)
                cell_y = int((y + dy * radius) // CELL_SIZE)
                if (cell_x < 0 or cell_x >= MAZE_WIDTH or
                    cell_y < 0 or cell_y >= MAZE_HEIGHT or
                    maze[cell_y][cell_x] == 'X'):
                    return True
        return False

    @staticmethod
    def find_path(maze, start, goal):
        astar = AStar(maze)
        path = astar.find_path(start, goal)
        return path

class AStar:
    def __init__(self, maze):
        self.maze = maze
        self.width = len(maze[0])
        self.height = len(maze)

    def heuristic(self, a, b):
        return abs(b[0] - a[0]) + abs(b[1] - a[1])

    def get_neighbors(self, node):
        x, y = node
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # 4-directional movement
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height and self.maze[ny][nx] != 'X':
                neighbors.append((nx, ny))
        return neighbors

    def find_path(self, start, goal):
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            current = heapq.heappop(frontier)[1]

            if current == goal:
                break

            for next in self.get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal, next)
                    heapq.heappush(frontier, (priority, next))
                    came_from[next] = current

        if goal not in came_from:
            return None

        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()
        return path