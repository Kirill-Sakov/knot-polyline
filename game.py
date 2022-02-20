"""General module with game."""
import random

import pygame

from game_colors import Colors
from knot import Knot
from point import Vec2d
from game_profile import profile_game

SCREEN_WIDTH = 820
SCREEN_HEIGHT = 640
SCREEN_DIM = (SCREEN_WIDTH, SCREEN_HEIGHT)


class Game:
    """Game implementation."""
    def __init__(self, steps=30):
        # Start parameters.
        self.working = True
        self.show_help = False
        self.pause = True
        pygame.init()
        self.gameDisplay = pygame.display.set_mode(SCREEN_DIM)
        pygame.display.set_caption("Polyline")
        # Curved line object.
        self.knot = Knot(steps)
        self.instruction = {
            "Show Help": "F1",
            "Restart": "R",
            "Pause/Play": "P",
            "More points": "Num+",
            "Less points": "Num-"
        }

    def run(self):
        """Loop cycle game."""
        while self.working:
            self.check_keys()
            self.gameDisplay.fill(Colors.BLACK)
            self.knot.change_color()
            self.knot.draw_points(self.gameDisplay)
            self.knot.draw(self.gameDisplay)
            if self.show_help:
                self.draw_help()
            pygame.display.flip()
            if self.pause:
                continue
            self.move_points()

    def check_keys(self):
        """Checking events from the user and changing states."""
        for game_event in pygame.event.get():
            if game_event.type == pygame.QUIT:
                self.working = False
            if game_event.type == pygame.KEYDOWN:
                if game_event.key == pygame.K_ESCAPE:
                    self.working = False
                if game_event.key == pygame.K_r:
                    self.restart()
                if game_event.key == pygame.K_p:
                    self.pause = not self.pause
                if game_event.key == pygame.K_F1:
                    self.show_help = not self.show_help
                if game_event.key == pygame.K_KP_PLUS:
                    self.knot.steps += 1
                if game_event.key == pygame.K_KP_MINUS:
                    self.knot.steps -= 1

            if game_event.type == pygame.MOUSEBUTTONDOWN:
                it = iter(game_event.pos)
                x = next(it)
                y = next(it)
                self.knot.base_points.append(Vec2d(x, y))
                self.knot.speeds.append(next(self.random_speed()))

    @staticmethod
    def random_speed():
        """Get random Point"""
        while True:
            yield Vec2d(random.random() * 2, random.random() * 2)

    def restart(self):
        """Restarting the game."""
        self.knot.base_points = []
        self.knot.points = []
        self.knot.speeds = []

    def draw_help(self):
        """Drawing help-screen."""
        self.gameDisplay.fill(Colors.GRAY)
        self.instruction.update({
            "Current steps": str(self.knot.steps),
            "Current points": str(len(self.knot.base_points))
        })
        # draw red borders
        corners = [0, 0, SCREEN_WIDTH, SCREEN_HEIGHT]
        pygame.draw.rect(self.gameDisplay, Colors.RED, corners, width=5)
        key_font = pygame.font.SysFont("courier", 24)
        command_font = pygame.font.SysFont("serif", 24)
        instruction_color = (128, 128, 255)
        for i, (command, key) in enumerate(self.instruction.items()):
            r_1 = key_font.render(key, True, instruction_color)
            r_2 = command_font.render(command, True, instruction_color)
            point1 = Vec2d(100, 100 + 30 * i)
            point2 = Vec2d(200, 100 + 30 * i)
            self.gameDisplay.blit(r_1, point1.int_pair())
            self.gameDisplay.blit(r_2, point2.int_pair())

    def move_points(self):
        """
        Move point and Reverses the movement of a point
        if it has gone off the screen.
        """
        for point, speed in zip(self.knot.base_points, self.knot.speeds):
            point += speed
            if self.is_limit_width(point):
                speed.reverse_x()
            if self.is_limit_height(point):
                speed.reverse_y()

    @staticmethod
    def is_limit_width(point: Vec2d):
        """Point is out of bounds."""
        return point.x > SCREEN_WIDTH or point.x < 0

    @staticmethod
    def is_limit_height(point: Vec2d):
        """Point is out of bounds."""
        return point.y > SCREEN_HEIGHT or point.y < 0


if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.display.quit()
    pygame.quit()
    exit(0)