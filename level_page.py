'''
@author: yangtau
@mail: yanggtau+fd@gmail.com
@brief:
    a page where plays select the level.
'''
import page_manager
import pygame_gui
import pygame
from resources.resource import load_image, load_json


class LevelPage(page_manager.PageBase):
    def __init__(self, pm, level_info_file: str):
        super().__init__(pm)
        self.__background = load_image("background/colored_forest_croped.png")
        self.__level_info = load_json(level_info_file)

    def __init_level_list(self):
        self.btn = pygame_gui.core.UIWindow(
            pygame.Rect(0, 0, 100, 200), self.gui_manager)

    def draw(self, window_surface):
        window_surface.blit(self.__background, (0, 0))


if __name__ == '__main__':
    pm = page_manager.PageManager((808, 700), 'level page')
    pm.push(LevelPage(pm, 'config/level.json'))
    pm.run()
