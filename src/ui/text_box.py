import pygame
from .component import Component
from . import utils

class TextBox(Component):
    def __init__(
            self,
            rect: pygame.Rect | tuple[int, int, int, int] | list[int],
            font:pygame.font.Font|None=None,
            color:tuple[int, int, int]|tuple[int, int, int, int]|list[int]=(0, 0, 0),
            background:tuple[int, int, int]|tuple[int, int, int, int]|list[int]=(0, 255, 255),
            border_color:tuple[int, int, int]|tuple[int, int, int, int]|list[int]=(0, 0, 0),
            border_radius:int=10,
            border_width:int=0,
            outer_surface: pygame.Surface | None = None
    ):
        """

        :param rect: (x, y, width, height)
        :param font: font use to render text
        :param color: text color
        :param background: background color
        :param border_color: use when border_width != 0
        :param border_radius:
        :param border_width:
        :param outer_surface:
        """
        super().__init__(rect, outer_surface)
        self.font = font if font is not None else pygame.font.Font(None, self.height)
        self.color = color
        self.background = background
        self.border_color = border_color
        self.border_radius = border_radius if border_radius >= 0 else 0
        self.border_width = border_width if border_width >= 0 else 0

        # default set empty
        self.set_text("")

    def set_text(self, text:str, align:tuple[int, int]|list[int]|None=None):
        """

        :param text:
        :param align: if align is None => centered text
        """
        pygame.draw.rect(self.surface, self.background, (0, 0, self.width, self.height), border_radius=self.border_radius)
        if self.border_width > 0:
            pygame.draw.rect(self.surface, self.border_color, (0, 0, self.width, self.height), width=self.border_width,  border_radius=self.border_radius)
        text_rendered = utils.render_text(text, self.font, self.color)
        if align is None:
            align = utils.get_center_offset(self.surface.get_size(), text_rendered.get_size())
        self.surface.blit(text_rendered, align)


