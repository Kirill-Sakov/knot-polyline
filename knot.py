#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List

import pygame

from game_colors import Colors
from point import Vec2d


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
            + (
                self.get_section_step(base_points, alpha, deg - 1)
                * (1 - alpha)
            )

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
        for point_one, point_two in zip(self.points[-1:] + self.points[:-1],
                                        self.points):
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
