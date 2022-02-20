#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List

import pygame
import random
import math

SCREEN_WIDTH = 820
SCREEN_HEIGHT = 640
SCREEN_DIM = (SCREEN_WIDTH, SCREEN_HEIGHT)


class Colors:
    """Game colors."""
    BLACK = (0, 0, 0)
    GRAY = (50, 50, 50)
    RED = (255, 50, 50, 255)
    WHITE = (255, 255, 255)


class Vec2d:
    """Realisation 2d Vector."""
    def __init__(self, x, y):
        self.x: float = x
        self.y: float = y

    def __str__(self):
        return f'{{x: {self.x}, y: {self.y}}}'

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Vec2d(x, y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Vec2d(x, y)

    def __mul__(self, num):
        x = self.x * num
        y = self.y * num
        return Vec2d(x, y)

    def __len__(self) -> float:
        """Vector length"""
        x = self.x ** 2
        y = self.y ** 2
        return math.sqrt(x + y)

    def int_pair(self) -> tuple:
        """Return tuple with current coordinates."""
        return self.x, self.y

    def is_limit_width(self):
        """Point is out of bounds."""
        return self.x > SCREEN_WIDTH or self.x < 0

    def is_limit_height(self):
        """Point is out of bounds."""
        return self.y > SCREEN_HEIGHT or self.y < 0

    def reverse_x(self):
        self.x = -self.x

    def reverse_y(self):
        self.y = -self.y


class Polyline:
    """Polyline Implementation."""
    def __init__(
            self,
            polyline_width: int = 3,
            polyline_color: pygame.Color = pygame.Color(255)
    ):
        self.base_points: List[Vec2d] = []
        self.speeds: List[Vec2d] = []
        self.width: int = polyline_width
        self.color: pygame.Color = polyline_color

    def append(self, point: Vec2d, speed: Vec2d):
        """Append polyline point."""
        self.base_points.append(point)
        self.speeds.append(speed)

    def move_points(self):
        """
        Move point and Reverses the movement of a point
        if it has gone off the screen.
        """
        for point, speed in zip(self.base_points, self.speeds):
            point += speed
            if point.is_limit_width():
                speed.reverse_x()
            if point.is_limit_height():
                speed.reverse_y()

    def draw_points(self, game_display, color=Colors.WHITE):
        """Draw current base points."""
        for point in self.base_points:
            pygame.draw.circle(game_display, color,
                               point.int_pair(),
                               self.width)

    def draw_line(self, game_display):
        """Draw sections between points."""
        for section in zip(self.base_points, self.base_points[1:]):
            point_one, point_two = section
            pygame.draw.line(game_display, self.color,
                             point_one.int_pair(),
                             point_two.int_pair(),
                             self.width)


class Knot(Polyline):
    """Curved Line Implementation."""
    def __init__(self, steps):
        """
        :param steps: Number of steps of each segment between base points
        """
        super().__init__()
        self._steps: int = steps
        self.points: List[Vec2d] = []
        self.hue = self.hue_generator()

    @property
    def steps(self) -> int:
        return self._steps

    @steps.setter
    def steps(self, value):
        """Steps cannot be less than 1."""
        if value < 1:
            return
        self._steps = value

    def calc_knot(self):
        """Calculation points of curved line."""
        # Draw only from 3 or more points.
        if len(self.base_points) < 3:
            return
        # Reinitialize point of curved line.
        self.points = []
        for first_point, second_point, third_point in self.cut_on_sections():
            # base points for section
            base_section_points = [(second_point + third_point) * 0.5,
                                   third_point,
                                   (third_point + first_point) * 0.5]
            knot_section = self.get_knot_section(base_section_points)
            self.points.extend(knot_section)

    def get_knot_section(self, base_points: List[Vec2d]) -> List[Vec2d]:
        """Calculating points of section curved line."""
        res = []
        alpha = 1 / self.steps
        for i in range(self.steps):
            res.append(self.get_section_step(base_points, alpha * i))
        return res

    def get_section_step(
            self,
            base_points: List[Vec2d],
            alpha: float,
            deg: int = None
    ) -> Vec2d:
        """Calculate step-section of section."""
        if deg is None:
            deg = len(base_points) - 1
        if deg == 0:
            return base_points[0]
        return (
                (base_points[deg] * alpha)
                + (self.get_section_step(base_points, alpha, deg - 1) * (1 - alpha))
        )

    def change_color(self):
        """Transfusion of color."""
        self.color.hsla = (next(self.hue), 100, 50, 100)

    @staticmethod
    def hue_generator() -> int:
        """Cycle-Generator between 0 and 360 with step 1."""
        hue = 0
        while True:
            hue += 1
            yield hue % 360

    def draw_line(self, game_display):
        """Draw sections between points."""
        for (point_one, point_two) in zip(self.points[-1:] + self.points[:-1], self.points):
            pygame.draw.line(game_display, self.color,
                             point_one.int_pair(),
                             point_two.int_pair(),
                             self.width)

    def draw(self, game_display):
        """Function drawing Polyline."""
        self.calc_knot()
        self.draw_line(game_display)

    def cut_on_sections(self):
        """Create sections from base points."""
        return zip(
            self.base_points[2:] + [self.base_points[0], self.base_points[1]],
            self.base_points,
            self.base_points[1:] + [self.base_points[0]]
        )


class Game:
    """Game implementation."""
    def __init__(self, steps=15):
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
            self.knot.move_points()  # Перерасчет точек

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


if __name__ == "__main__":
    import cProfile, pstats
    profiler = cProfile.Profile()
    profiler.enable()
    game = Game()
    game.run()
    pygame.display.quit()
    pygame.quit()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats()
    exit(0)
