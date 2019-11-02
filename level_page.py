'''
@author: yangtau
@mail: yanggtau+fd@gmail.com
@brief:
    This is a page where plays select the level
'''
import page_manager
import pygame_gui
import pygame
from resources.resource import load_image, load_json


class LevelPage(page_manager.PageBase):
    def __init__(self, pm, level_info_file: str):
        super().__init__(pm)
        self.__background = load_image("background/colored_forest_croped.png")

    def draw(self, window_surface):
        window_surface.blit(self.__background, (0, 0))


if __name__ == '__main__':
    pm = page_manager.PageManager((808, 700), 'level page')
    pm.push(LevelPage(pm, ''))
    pm.run()
