import pygame
import warnings
from typing import List, Union

from .. import ui_manager
from ..core import ui_container
from ..core.ui_element import UIElement


class UILabel(UIElement):
    """
    A label lets us display a single line of text with a single font style. It's a quick to redraw and simple
    alternative to the text box element.

    :param relative_rect: The rectangle that contains and positions the label relative to it's container.
    :param text: The text to display in the label.
    :param manager: The UIManager that manages this label.
    :param container: The container that this element is within. If set to None will be the root window's container.
    :param element_ids: A list of ids that describe the 'journey' of UIElements that this UIElement is part of.
    :param object_id: A custom defined ID for fine tuning of theming.
    """
    def __init__(self, relative_rect: pygame.Rect, text: str, manager: ui_manager.UIManager,
                 container: ui_container.UIContainer = None,
                 element_ids: Union[List[str], None] = None, object_id: Union[str, None] = None):
        if element_ids is None:
            new_element_ids = ['label']
        else:
            new_element_ids = element_ids.copy()
            new_element_ids.append('label')
        super().__init__(relative_rect, manager, container,
                         starting_height=1,
                         layer_thickness=1,
                         object_id=object_id,
                         element_ids=new_element_ids)
        self.text = text
        self.redraw()

    def set_text(self, text: str):
        """
        Changes the string displayed by the label element. Labels do not support HTML styling.

        :param text: the text to set the label to.
        """
        self.text = text
        self.redraw()

    def redraw(self):
        """
        Re-render the text to the label's underlying sprite image. This allows us to change what the displayed text is
        or remake it with different theming (if the theming has changed).
        """
        font = self.ui_theme.get_font(self.object_id, self.element_ids)
        text_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'normal_text')
        bg_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'dark_bg')
        text_shadow_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'text_shadow')

        shadow_enabled = False
        shadow_enable_param = self.ui_theme.get_misc_data(self.object_id, self.element_ids, 'text_shadow')
        if shadow_enable_param is not None:
            shadow_enabled = bool(int(shadow_enable_param))

        shadow_size = 1
        shadow_size_param = self.ui_theme.get_misc_data(self.object_id, self.element_ids, 'text_shadow_size')
        if shadow_size_param is not None:
            shadow_size = int(shadow_size_param)

        shadow_offset = [0, 0]
        shadow_offset_param = self.ui_theme.get_misc_data(self.object_id, self.element_ids, 'text_shadow_offset')
        if shadow_offset_param is not None:
            offset_string_list = shadow_offset_param.split(',')
            if len(offset_string_list) == 2:
                shadow_offset = [int(offset_string_list[0]), int(offset_string_list[1])]

        text_size = font.size(self.text)
        if text_size[1] > self.rect.height or text_size[0] > self.rect.width:
            width_overlap = self.rect.width - text_size[0]
            height_overlap = self.rect.height - text_size[1]
            warn_text = 'Label Rect is too small for text: ' + self.text + ' - size diff: ' + str((width_overlap,
                                                                                                   height_overlap))
            warnings.warn(warn_text, UserWarning)

        if bg_colour.a != 255 or shadow_enabled:
            text_render = font.render(self.text, True, text_colour)
        else:
            text_render = font.render(self.text, True, text_colour, bg_colour)
        text_render_rect = text_render.get_rect(centerx=self.rect.width/2, centery=self.rect.height/2)
        self.image = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)
        self.image.fill(bg_colour)

        if shadow_enabled:
            shadow_text_render = font.render(self.text, True, text_shadow_colour)

            for y in range(-shadow_size, shadow_size+1):
                shadow_text_render_rect = pygame.Rect((text_render_rect.x + shadow_offset[0],
                                                       text_render_rect.y + shadow_offset[1] + y),
                                                      text_render_rect.size)
                self.image.blit(shadow_text_render, shadow_text_render_rect)

            for x in range(-shadow_size, shadow_size+1):
                shadow_text_render_rect = pygame.Rect((text_render_rect.x + shadow_offset[0] + x,
                                                       text_render_rect.y + shadow_offset[1]), text_render_rect.size)
                self.image.blit(shadow_text_render, shadow_text_render_rect)

            for x_and_y in range(-shadow_size, shadow_size+1):
                shadow_text_render_rect = pygame.Rect((text_render_rect.x + shadow_offset[0] + x_and_y,
                                                       text_render_rect.y + shadow_offset[1] + x_and_y),
                                                      text_render_rect.size)
                self.image.blit(shadow_text_render, shadow_text_render_rect)

            for x_and_y in range(-shadow_size, shadow_size+1):
                shadow_text_render_rect = pygame.Rect((text_render_rect.x + shadow_offset[0] - x_and_y,
                                                       text_render_rect.y + shadow_offset[1] + x_and_y),
                                                      text_render_rect.size)
                self.image.blit(shadow_text_render, shadow_text_render_rect)

        self.image.blit(text_render, text_render_rect)
