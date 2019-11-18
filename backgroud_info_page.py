'''
@author: yangtau
@email: yanggtau+fd@gmail.com
@brief:

'''
from page_manager import PageBase, PageManager
from level_page import LevelPage
import pygame_gui
import pygame
from resources.resource import FONTS_DIR, load_image, SETTINGS
import common


class BackgroundInfoPage(PageBase):
    size = common.WIN_SIZE
    text_size = (700, 500)
    text_pos = ((size[0]-text_size[0])//2, 50)
    btn_size = (160, 60)
    btn_pos = ((size[0]-btn_size[0])//2, 600)

    def __init__(self, pm: PageManager):
        super().__init__(pm)
        self.__background = load_image(SETTINGS['background'])
        self.__init_text()
        btn = pygame_gui.elements.UIButton(
            pygame.Rect(self.btn_pos, self.btn_size),
            '跳过',
            self.gui_manager
        )
        self.register_gui_event_handler(
            'ui_button_pressed', btn,
            lambda e: self.page_manager.replace(LevelPage(self.page_manager))
        )

    def __init_text(self):
        self.gui_manager.add_font_paths(
            'noto-sans', FONTS_DIR+'NotoSansCJK-Regular.ttc')
        self.gui_manager.preload_fonts(
            [{'name': 'noto-sans', 'point_size': 24, 'style': 'regular'}])
        self.__text = pygame_gui.elements.UITextBox(
            '<font face=noto-sans size=6.0 color=#111111ff>'
            '在很久以前，一位漂亮的公主被大魔王抓走了。<br>'
            '勇敢的英雄为了拯救美丽的公主，踏上了一条xx的道路<br>'
            '...<br>'
            '你能帮助大魔王打败英雄吗<br>'
            '你能帮助大魔王打败英雄吗<br>'
            '你能帮助大魔王打败英雄吗<br>'
            '你能帮助大魔王打败英雄吗<br>'
            '你能帮助大魔王打败英雄吗<br>'
            '你能帮助大魔王打败英雄吗<br>'
            '你能帮助大魔王打败英雄吗<br>'
            '你能帮助大魔王打败英雄吗<br>'
            '你能帮助大魔王打败英雄吗<br>'
            '你能帮助大魔王打败英雄吗<br>'
            '</font>',
            pygame.Rect(self.text_pos, self.text_size),
            self.gui_manager
        )
        self.__text.set_active_effect('typing_appear')

    def draw(self, window_surface):
        window_surface.blit(self.__background, (0, 0))


if __name__ == '__main__':
    pm = PageManager(common.WIN_SIZE, 'hello')
    pm.push(BackgroundInfoPage(pm))
    pm.run()
