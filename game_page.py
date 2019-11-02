'''
@author: yangtau
@mail: yanggtau+fd@gmail.com
@brief:
    the page where players play the game
'''
import pygame
import pygame_gui
from collections import defaultdict
import surfaces
import page_manager 
from resources.resource import load_json
from resources.resource import load_image


class Button(object):
    def __init__(self):
        self.__state1 = load_image('button/pause.png')
        self.__state0 = load_image('button/start.png')
        self.rect = self.__state1.get_rect()
        self.__state = 0

    @property
    def image(self):
        if self.__state == 0:
            return self.__state0
        else:
            return self.__state1

    def click(self):
        self.__state = 1-self.__state


class GamePage(page_manager.PageBase):
    def __init__(self, pm, map_config_file: str, toolbox_config_file: str):
        super().__init__(pm)
        self.__map = surfaces.Map(map_config_file, (20, 20))
        self.__toolbox = surfaces.Toolbox(toolbox_config_file, (20, 616))
        self.__surface = pygame.Surface((808, 700), pygame.SRCALPHA, 32)
        # button
        self.__start = False
        self.__btn = Button()
        self.__btn.rect.center = (756, 648)
        self.tool_in_mouse = None
        self.force_refresh = False
        # register event handlers
        self.register_event_handler(pygame.MOUSEBUTTONDOWN, self.btn_click)
        self.register_event_handler(pygame.MOUSEBUTTONDOWN, self.drag_handler)

    def btn_click(self, event):
        btn = self.__btn
        if event.button == 1 and btn.rect.collidepoint(pygame.mouse.get_pos()):
            btn.click()
            if not self.__start:
                self.__start = True
                self.__map.start()
            else:
                self.__start = False
                self.__map.reset()

    def drag_handler(self, event):
        # click left
        if event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.__map.rect.collidepoint(mouse_pos):
                if self.tool_in_mouse:
                    # put down a tool
                    # TODO: what if there is already a tool in the mouse_pos
                    self.__map.put_tool(mouse_pos, self.tool_in_mouse)
                    self.tool_in_mouse = None
                else:
                    # remove tool
                    self.__map.remove_tool(mouse_pos)
            if self.__toolbox.rect.collidepoint(mouse_pos):
                if not self.tool_in_mouse:
                    self.tool_in_mouse = self.__toolbox.get_tool(mouse_pos)
                    self.tool_in_mouse.rect = self.tool_in_mouse.texture.get_rect()
        # click right
        if event.button == 3:
            # throw away tool in hand
            if self.tool_in_mouse:
                self.tool_in_mouse = None
                self.force_refresh = True

    def draw(self, window_surface):
        window_surface.fill((255, 255, 255))
        # if self.tool_in_mouse or self.force_refresh:
        #     self.surface.fill((255, 255, 255))
        self.__map.draw(window_surface)
        self.__toolbox.draw(window_surface)
        window_surface.blit(self.__btn.image, self.__btn.rect)
        # draw mouse
        if self.tool_in_mouse:
            self.tool_in_mouse.rect.center = pygame.mouse.get_pos()
            window_surface.blit(self.tool_in_mouse.texture,
                                self.tool_in_mouse.rect)
        self.force_refresh = False
