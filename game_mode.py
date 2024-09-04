class GameMode: 
    def __init__(self, game):
        self.game = game

    def update(self):
        pass

    def render(self, screen):
        pass

    def handle_event(self, event):
        pass

    @staticmethod
    def lerp_color(color1, color2, t):
        return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))
