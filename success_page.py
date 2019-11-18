'''
@author: yangtau
@email: yanggtau+fd@gmail.com
@brief:

'''
from page_manager import PageBase, PageManager
import game_page
from sprites import Hero, Princess
from resources.resource import get_font, load_image, load_json, SETTINGS
import pygame
import pygame_gui
import common


class SuccessPage(PageBase):
    size = common.WIN_SIZE
    # title
    title_y_off = 100
    title_str = '胜利'
    title_text_size = 50
    title_color = (100, 100, 200)
    # btn
    btn_size = (150, 60)
    btn_margin = 50
    btn_y_off = 450

    def __init__(self, pm: PageManager, level_name: str):
        super().__init__(pm)
        self.__level_name = level_name
        # next_level: (map_json, toolbox_json)
        self.__next_level = self.__get_next_level(level_name)
        self.__background = load_image(SETTINGS['background'])
        self.__init_title()
        self.__init_btn()

    def __get_next_level(self, level):
        '''Return the map json and toolbox json of the next level'''
        level_info = load_json('config/level.json')
        for i in range(len(level_info)):
            if level_info[i]['name'] == level:
                break
        i += 1
        if i < len(level_info):
            return level_info[i]['map'], level_info[i]['name']
        return None

    def __init_btn(self):
        btn_x_off = (self.size[0]-self.btn_size[0]*2-self.btn_margin)//2
        next_level_btn = pygame_gui.elements.UIButton(
            pygame.Rect((btn_x_off, self.btn_y_off), self.btn_size),
            '下一关',
            self.gui_manager
        )
        # disable next_btn if this is the last level
        if not self.__next_level:
            next_level_btn.disable()
        self.register_gui_event_handler(
            'ui_button_pressed', next_level_btn,
            lambda e: self.page_manager.replace(
                game_page.GamePage(self.page_manager, *self.__next_level)
            )
        )
        quit_btn = pygame_gui.elements.UIButton(
            pygame.Rect(
                (btn_x_off+self.btn_size[0]+self.btn_margin, self.btn_y_off), self.btn_size),
            '退出',
            self.gui_manager
        )
        self.register_gui_event_handler(
            'ui_button_pressed', quit_btn,
            lambda e: self.page_manager.pop())

    def __init_title(self):
        font = get_font('noto-sans-bold', self.title_text_size)
        text = font.render(
            self.title_str, True, self.title_color)
        self.__title_text = text
        self.__title_pos = ((self.size[0]-text.get_width())//2,
                            self.title_y_off)

    def draw(self, window_surface):
        window_surface.blit(self.__background, (0, 0))
        window_surface.blit(self.__title_text, self.__title_pos)


if __name__ == '__main__':
    pm = PageManager(common.WIN_SIZE, 'Hello')
    pm.push(FailPage(pm, ''))
    pm.run()
