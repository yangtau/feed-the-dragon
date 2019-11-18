'''
@author: yangtau
@email: yanggtau+fd@gmail.com
@brief:
    the entrance page of the game
'''
import pygame_gui
import pygame
from backgroud_info_page import BackgroundInfoPage
from page_manager import PageManager, PageBase
from map_editor_page import EditorPage
from resources.resource import load_json, load_image, get_font, SETTINGS, play_bgm 
import common


class StartPage(PageBase):
    size = common.WIN_SIZE
    # button size and pos
    btn_size = (160, 60)
    btn_margin = 30
    btn_y_off = 300
    btn_x_off = (size[0] - btn_size[0]) / 2
    # title
    title_y_off = 30
    title_str = '拯救大魔王'
    title_text_size = 50
    title_color = (120, 120, 255)

    def __init__(self, pm: PageManager):
        super().__init__(pm)
        # background
        self.__background = load_image(SETTINGS['background'])
        # init button
        self.__init_btn()
        self.__init_title()
        play_bgm()

    def __init_title(self):
        font = get_font('noto-sans-bold', self.title_text_size)
        text = font.render(
            self.title_str, True, self.title_color)
        self.__title_text = text
        self.__title_pos = ((self.size[0]-text.get_width())//2,
                            self.title_y_off)

    def __init_btn(self):
        btn_rect = [pygame.Rect((self.btn_x_off, self.btn_y_off +
                                 (self.btn_margin+self.btn_size[1])*i),
                                self.btn_size) for i in range(4)]
        # start button
        self.__start_btn = pygame_gui.elements.UIButton(
            btn_rect[0], "开始!", self.gui_manager)
        self.register_gui_event_handler(
            'ui_button_pressed',
            self.__start_btn,
            lambda e: self.page_manager.push(BackgroundInfoPage(self.page_manager)))
        # setting button
        self.__setting_btn = pygame_gui.elements.UIButton(
            btn_rect[1], "设置", self.gui_manager)
        self.register_gui_event_handler(
            'ui_button_pressed',
            self.__setting_btn,
            lambda e: print('setting'))
        # map editor button
        self.__map_editor_btn = pygame_gui.elements.UIButton(
            btn_rect[2], "地图编辑", self.gui_manager)
        self.register_gui_event_handler(
            'ui_button_pressed',
            self.__map_editor_btn,
            lambda e: self.page_manager.push(EditorPage(self.page_manager)))
        # quit button
        self.__quit_btn = pygame_gui.elements.UIButton(
            btn_rect[3], "退出", self.gui_manager)
        self.register_gui_event_handler('ui_button_pressed',
                                        self.__quit_btn,
                                        lambda e: self.page_manager.pop())

    def draw(self, window_surface):
        window_surface.blit(self.__background, (0, 0))
        window_surface.blit(self.__title_text, self.__title_pos)


if __name__ == '__main__':
    page_manager = PageManager((808, 700), 'Hello')
    page_manager.push(StartPage(page_manager))
    page_manager.run()