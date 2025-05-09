import pygame
from PIL import Image

def blit_centered(outer_surface:pygame.Surface, inner_surface:pygame.Surface):
    pos = get_center_offset(outer_size=outer_surface.get_size(), inner_size=inner_surface.get_size())
    outer_surface.blit(inner_surface, pos)

def get_center_offset(outer_size:tuple[int, int]|list[int], inner_size:tuple[int, int]|list[int])->tuple[int, int]:
    x, y = 0, 0
    if inner_size[0] < outer_size[0]:
        x = (outer_size[0] - inner_size[0]) // 2
    if inner_size[1] < outer_size[1]:
        y = (outer_size[1] - inner_size[1]) // 2
    return x, y

def scale_surface_to_fit(surface: pygame.Surface, max_size: tuple[int, int]) -> pygame.Surface:
    original_width, original_height = surface.get_size()
    if original_width <= 0 or original_height <= 0 or max_size[0] <=0 or max_size[1] <= 0:
        return surface

    max_width, max_height = max_size

    scale_w = max_width / original_width
    scale_h = max_height / original_height

    scale = min(scale_w, scale_h, 1.0)

    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    return pygame.transform.smoothscale(surface, (new_width, new_height))

def gif_to_surfaces(gif_path):
    pil_image = Image.open(gif_path)
    surfaces = []
    try:
        while True:
            frame = pil_image.copy()
            frame = frame.convert("RGBA")
            frame_data = frame.tobytes()
            surface = pygame.image.fromstring(frame_data, frame.size, 'RGBA')
            surfaces.append(surface)
            pil_image.seek(pil_image.tell() + 1)
    except EOFError:
        pass
    return surfaces

def render_text(
        text:str,
        font:pygame.font.Font,
        color:tuple[int, int, int]|tuple[int, int, int, int]|list[int]=(0, 0, 0),
        antialias:bool=True,
        background: tuple[int, int, int]|tuple[int, int, int, int]|list[int]|None=None,
        line_spacing:int = 10
)->pygame.Surface:
    """
    This function should be used when rendering multi-line text that includes newline (\n) characters.
    :param text:
    :param font:
    :param color:
    :param antialias:
    :param background:
    :param line_spacing:
    :return:
    """

    lines = text.split(sep='\n')
    lines = [l for l in lines if l != '']

    rendered_lines = []
    width, height = 0 ,0

    for line in lines:
        l = font.render(line, antialias, color, background)
        rendered_lines.append(l)
        width = max(width, l.get_width())
        height = max(height, l.get_height() + line_spacing)

    result = pygame.Surface((width, height*len(rendered_lines)), pygame.SRCALPHA)
    if background is not None:
        result.fill(background)

    for i in range(len(rendered_lines)):
        result.blit(rendered_lines[i], (0, height*i))

    return result

def generate_relative_rect(
        rect:pygame.Rect|tuple[int, int, int, int]|list[int],
        size:tuple[int, int]|list[int],
        position:str='left',
        spacing:int=10,
)->tuple[int, int, int, int]:
    """

    :param rect: The base rectangle to which the new rectangle will be positioned.
    :param size: Width and height of the new rectangle.
    :param position: Relative position of the new rectangle. Must be one of:'left', 'right', 'top', or 'bottom'. Defaults to 'left'.
    :param spacing: The space between the base rectangle and the new one. Defaults to 10.
    :return:
    """
    x, y, w, h = 0, 0, size[0], size[1]

    if spacing < 0:
        spacing = 0

    if position == 'left':
        x = rect[0] - w - spacing
        y = rect[1]

    elif position == 'right':
        x = rect[0] + rect[2] + spacing
        y = rect[1]

    elif position == 'top':
        x = rect[0]
        y = rect[1] - h - spacing

    elif position == 'bottom':
        x = rect[0]
        y = rect[1] + rect[3] + spacing

    else:
        raise RuntimeError("Position must be left/right/top/bottom")

    return x, y, w, h