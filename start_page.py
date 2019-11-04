'''
@author: yangtau
@email: yanggtau+fd@gmail.com
@brief:
    the entrance page of the game
'''
import page_manager as pm
import pygame_gui
import pygame
import game_page
import level_page
from resources.resource import load_json, load_image, FONTS_DIR, THEME_DIR, get_font


class StartPage(pm.PageBase):
    size = (808, 700)
    # button size and pos
    btn_size = (160, 60)
    btn_margin = 40
    btn_y_off = 300
    btn_x_off = (size[0] - btn_size[0]) / 2
    # title
    title_y_off = 30
    title_str = '拯救大魔王'
    title_text_size = 50
    title_color = (120, 120, 255)

    def __init__(self, pm: pm.PageManager):
        super().__init__(pm)
        # self.gui_manager.set_theme(THEME_DIR+'theme.json')
        # background
        self.__background = load_image("background/colored_forest_croped.png")
        # init button
        self.__init_btn()
        self.__init_title()

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
        lp = level_page.LevelPage(self.page_manager, 'config/level.json')
        self.register_gui_event_handler(
            'ui_button_pressed',
            self.__start_btn,
            lambda e: self.page_manager.push(lp))
        # setting button
        self.__setting_btn = pygame_gui.elements.UIButton(
            btn_rect[1], "设置", self.gui_manager)
        self.register_gui_event_handler('ui_button_pressed',
                                        self.__setting_btn,
                                        lambda e: print('setting'))
        # map editor button
        self.__map_editor_btn = pygame_gui.elements.UIButton(
            btn_rect[2], "地图编辑", self.gui_manager)
        self.register_gui_event_handler('ui_button_pressed',
                                        self.__map_editor_btn,
                                        lambda e: print('map editor'))
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
    page_manager = pm.PageManager((808, 700), 'Hello')
    page_manager.push(StartPage(page_manager))
    page_manager.run()
