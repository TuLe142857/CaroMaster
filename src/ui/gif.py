import pygame
from .component import Component
from . import utils

class Gif(Component):
    def __init__(
            self,
            rect: pygame.Rect | tuple[int, int, int, int] | list[int],
            frames:list[pygame.Surface],
            frame_delay:int=1,
            outer_surface: pygame.Surface | None = None
    ):
        """

        :param rect: (x, y, width, height)
        :param frames:  A list of surfaces representing each frame of the animation.
        :param frame_delay: Number of render cycles to wait before switching to the next frame.
        :param outer_surface:
        """
        super().__init__(rect, outer_surface)
        self.frames = [utils.scale_surface_to_fit(f, (self.width, self.height)) for f in frames]
        self.frame_delay = frame_delay
        self.count = 0
        self.current_frame = 0

        self.draw_frame()

    def draw_frame(self):
        self.surface.fill((0, 0, 0, 0))
        self.surface.blit(self.frames[self.current_frame], (0, 0))

    def render(self):
        self.count += 1
        if self.count == self.frame_delay:
            self.count = 0
            self.current_frame = (self.current_frame+1) % len(self.frames)
            self.draw_frame()
        super().render()
