import json
from constants import MAZE_WIDTH, MAZE_HEIGHT

class LevelManager:
    def __init__(self, levels_file):
        self.levels_file = levels_file
        self.levels = []
        self.current_level_index = 0

    def load_levels_from_file(self):
        with open(self.levels_file, 'r') as f:
            levels_data = json.load(f)
        self.levels = [Level(level_data["maze"], level_data["level_number"], level_data.get("title", "")) for level_data in levels_data]
        if self.levels and not self.levels[0].title:
            self.levels[0].title = "The Zig Zag"
        if len(self.levels) > 1 and not self.levels[1].title:
            self.levels[1].title = "The Swirl"
        print(f"Levels loaded from {self.levels_file}")

    def save_levels_to_file(self):
        levels_data = [{"maze": level.maze, "level_number": level.level_number, "title": level.title} for level in self.levels]
        with open(self.levels_file, 'w') as f:
            json.dump(levels_data, f)
        print(f"Levels saved to {self.levels_file}")

    def get_current_level(self):
        return self.levels[self.current_level_index]

    def next_level(self):
        self.current_level_index = (self.current_level_index + 1) % len(self.levels)
        return self.get_current_level()

    def prev_level(self):
        self.current_level_index = (self.current_level_index - 1) % len(self.levels)
        return self.get_current_level()

    def new_level(self):
        new_maze = [['X' for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)]
        self.levels.append(Level(new_maze, len(self.levels) + 1))
        self.current_level_index = len(self.levels) - 1
        return self.get_current_level() 
    

class Level:
    def __init__(self, maze, level_number, title=""):
        self.maze = maze
        self.level_number = level_number
        self.title = title