import pygame
from . import utils
from .component import Component

class Board(Component):
    def __init__(
            self,
            x:int,
            y:int,
            rows:int,
            columns:int,
            cell_size:int,
            font:pygame.font.Font|None = None,
            background:tuple[int, int, int]|tuple[int, int, int, int]|list[int]=(255, 255, 255),
            line_color: tuple[int, int, int] | tuple[int, int, int, int] | list[int] = (0, 0, 0),
            line_width:int=1,
            outer_surface: pygame.Surface | None = None
    ):
        if rows <= 0 or columns <= 0:
            raise RuntimeError("Invalid value")

        super().__init__((x, y, rows*cell_size, columns*cell_size), outer_surface)
        self.rows = rows
        self.columns = columns
        self.cell_size = cell_size
        self.font = font if font is not None else pygame.font.Font(None, self.cell_size)
        self.background = background
        self.line_color = line_color
        self.line_width = line_width if line_width >= 1 else 1

        self.clear()

    def cell_detect(self, coordinate:tuple[int, int]|list[int])->tuple[int, int]:
        """
        :param coordinate: coordinate on outer surface
        :return: tuple(row, column)
        """
        coord = self.convert_coordinate(coordinate)

        row = coord[1]//self.cell_size
        col = coord[0]//self.cell_size
        return row, col


    def clear(self):
        """
        set all cells EMPTY
        """
        self.surface.fill(self.background)

        # border
        pygame.draw.rect(self.surface, self.line_color, (0, 0, self.width, self.height), width=self.line_width)

        # horizontal line
        for row in range(1, self.rows):
            start = (0, row * self.cell_size)
            end = (self.width, row * self.cell_size)
            pygame.draw.line(self.surface, self.line_color, start, end, width=self.line_width if row%5!=0 else (self.line_width*2))

        # vertical line
        for col in range(1, self.columns):
            start = (col * self.cell_size, 0)
            end = (col * self.cell_size, self.height)
            pygame.draw.line(self.surface, self.line_color, start, end, width=self.line_width if col%5!=0 else (self.line_width*2))


    def put(
            self,
            piece:str,
            position:tuple[int, int]|list[int],
            color: tuple[int, int, int]|tuple[int, int, int, int]|list[int] = (0, 0, 0),
            background: tuple[int, int, int] | tuple[int, int, int, int] | list[int] = (255, 255,255)
    ):
        """

        :param piece:
        :param position: tuple[row, column]
        :param color:
        :param background:
        :return:
        """
        row, column = position
        x = column * self.cell_size + self.line_width
        y = row * self.cell_size + self.line_width
        w = self.cell_size - self.line_width
        h = self.cell_size - self.line_width
        if column % 5 == 0 and column != 0:
            x += self.line_width
            w -= self.line_width
        if row % 5 == 0 and row != 0:
            y += self.line_width
            h -= self.line_width
        if column == self.columns -1:
            w -= self.line_width
        if row == self.rows -1:
            h -= self.line_width

        text_rendered = self.font.render(piece, True, color)
        align = utils.get_center_offset(outer_size=(w, h), inner_size=text_rendered.get_size())

        pygame.draw.rect(self.surface, background, (x, y, w, h))
        self.surface.blit(text_rendered, (x + align[0], y + align[1]))