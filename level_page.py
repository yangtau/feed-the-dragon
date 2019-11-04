'''
@author: yangtau
@mail: yanggtau+fd@gmail.com
@brief:
    a page where plays select the level.
'''
import pygame_gui
import pygame
from resources.resource import load_image, load_json, get_font
from game_page import GamePage
from page_manager import PageManager, PageBase


class LevelPage(PageBase):
    size = (808, 700)
    # level list
    level_list_width = 300
    level_list_item_height = 50
    level_list_rect = pygame.Rect(
        (size[0] - level_list_width) // 2, 250,
        level_list_width, level_list_item_height)
    # title
    title_y_off = 30
    title_str = '选择关卡'
    title_text_size = 50
    title_color = (120, 120, 255)

    def __init__(self, pm):
        super().__init__(pm)
        self.__background = load_image("background/colored_forest_croped.png")
        self.__level_info = load_json('config/level.json')
        self.__init_level_list()
        self.__init_title()

    def __init_title(self):
        font = get_font('noto-sans-bold', self.title_text_size)
        text = font.render(
            self.title_str, True, self.title_color)
        self.__title_text = text
        self.__title_pos = ((self.size[0]-text.get_width())//2,
                            self.title_y_off)

    def __init_level_list(self):
        xs = [x['name'] for x in self.__level_info]
        self.__level_info = {a: b for a, b in zip(xs, self.__level_info)}
        drop_down = pygame_gui.elements.UIDropDownMenu(
            xs, xs[0], 'expanded',
            self.level_list_rect, self.gui_manager)
        self.register_gui_event_handler(
            'ui_drop_down_menu_changed', drop_down, self.__list_event_handle)

    def __list_event_handle(self, event):
        level_name = event.text
        self.page_manager.replace(GamePage(
            self.page_manager,
            self.__level_info[level_name]['map'],
            self.__level_info[level_name]['toolbox']
        ))

    def draw(self, window_surface):
        window_surface.blit(self.__background, (0, 0))
        window_surface.blit(self.__title_text, self.__title_pos)


if __name__ == '__main__':
    pm = PageManager((808, 700), 'level page')
    pm.push(LevelPage(pm))
    pm.run()
