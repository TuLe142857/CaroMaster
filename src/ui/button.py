import pygame
from typing import Any
from .component import Component
from . import utils

class Button(Component):
    def __init__(
            self,
            rect:pygame.Rect|tuple[int, int, int, int]|list[int],
            label:pygame.Surface|str="button",
            font:pygame.font.Font|None=None,
            background:dict[str, Any]|None = None,
            color:dict[str, Any]|None = None,
            border_color:dict[str, Any]|None = None,
            border_radius:int=10,
            border_width:int=0,
            outer_surface:pygame.Surface|None = None
    ):
        super().__init__(rect, outer_surface)
        self.label = label
        self.font = font if font is not None else pygame.font.Font(None, self.height)
        self.background = background if background is not None else  {'normal':(0, 255, 0, 128), 'hover':(0, 255, 255, 128)}
        self.color = color if color is not None else {'normal':(0, 0, 0), 'hover':(0, 0, 0)}
        self.border_color = border_color if border_color is not None else {'normal':(0, 0, 0), 'hover':(255, 255, 0)}
        self.border_radius = border_radius if border_radius >= 0 else 0
        self.border_width = border_width if border_width >= 0 else 0

        self.status = 'normal' # use to handle event (pygame.MOUSEMOTION)
        self.update()

    def update(self):
        pygame.draw.rect(self.surface, self.background[self.status], (0, 0, self.width, self.height), border_radius=self.border_radius)
        if self.border_width > 0:
            pygame.draw.rect(self.surface, self.border_color[self.status], (0, 0, self.width, self.height), width=self.border_width,border_radius=self.border_radius)

        if isinstance(self.label, str):
            text_rendered = self.font.render(self.label, True, self.color[self.status])
            utils.blit_centered(outer_surface=self.surface, inner_surface=text_rendered)
        else:

            utils.blit_centered(outer_surface=self.surface, inner_surface= utils.scale_surface_to_fit(self.label, (self.width, self.height)))

    def handle_event(self, e:pygame.event.Event):
        super().handle_event(e)

        if e.type == pygame.MOUSEMOTION:
            is_inside = self.contain_coordinate(pygame.mouse.get_pos())
            if is_inside and self.status != 'hover':
                self.status = 'hover'
                self.update()
            elif not is_inside and self.status != 'normal':
                self.status = 'normal'
                self.update()