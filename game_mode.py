from constants import WIDTH, HEIGHT

class GameMode: 
    def __init__(self, game):
        self.game = game

    def update(self):
        pass

    def render(self, screen):
        pass

    def handle_event(self, event):
        pass

    def get_screen_scale(self, screen):
        """Returns scale factor based on current screen size"""
        return min(screen.get_width()/WIDTH, screen.get_height()/HEIGHT)

    @staticmethod
    def lerp_color(color1, color2, t):
        return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))
