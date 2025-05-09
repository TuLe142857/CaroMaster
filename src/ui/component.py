from typing import Callable, Any
import pygame

class Component:
    def __init__(
            self,
            rect:pygame.Rect|tuple[int, int, int, int]|list[int],
            outer_surface:pygame.Surface|None = None
    ):
        """

        :param rect: (x, y, width, height)
        :param outer_surface: if value is None, outer_surface = pygame.display.get_surface()
        :return:
        """
        x, y, w, h = rect
        self.x = x if x >= 0 else 0
        self.y = y if y >= 0 else 0
        self.width = w if w >= 0 else 0
        self.height = h if h >= 0 else 0
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.outer_surface = outer_surface if outer_surface is not None else pygame.display.get_surface()
        self.event_handlers = []

    def rect(self)->tuple[int, int, int, int]:
        return self.x, self.y, self.width, self.height

    def render(self):
        self.outer_surface.blit(self.surface, (self.x, self.y))

    def handle_event(self, e:pygame.event.Event):
        for action in self.event_handlers:
            action(e)

    def add_event_handler(self, action:Callable[[pygame.event.Event], Any]):
        self.event_handlers.append(action)

    def convert_coordinate(self, coordinate:tuple[int, int]|list[int])->tuple[int, int]:
        """

        :param coordinate: coordinate on outer surface
        :return: coordinate  on self.surface
        """
        return coordinate[0] - self.x, coordinate[1] - self.y

    def contain_coordinate(self, coordinate:tuple[int, int]|list[int])->bool:
        """

        :param coordinate: coordinate on outer surface
        :return: if coordinate is inside this component
        """
        coord = self.convert_coordinate(coordinate)
        return (0 <=  coord[0] < self.width) and (0 <= coord[1] < self.height)