# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 09:17:12 2019
@file:  mapEditor_page.py
@brief: this file is a page which maneges the map_editor

@author: 冯准生
@email:1565853379@qq.com
"""

import pygame
import pygame_gui
import page_manager as pm
from resources.resource import load_json
from resources.resource import load_image
import mapEditor

class EditorPage(pm.PageBase):
    def __init__(self, pm, map_config_file: str, toolbox_config_file: str):
        super().__init__(pm)
        self.__map = mapEditor.Map_base(map_config_file, (20, 20))
        self.__elembox = mapEditor.Elem_base(toolbox_config_file, (20, 616))
        self.__background = load_image('background/colored_forest_croped.png')
        self.tool_in_mouse = None
        self.force_refresh = False
        self.register_event_handler(pygame.MOUSEBUTTONDOWN, self.drag_handler)
        self.__init_btn()
    
    def __init_btn(self):
        btn_rect = pygame.Rect(756, 648,(160,60))
        self.__end_btn = pygame_gui.elements.UIButton(
            btn_rect[0], "完成!", self.gui_manager)
        lp = MapNamePage(self.page_manager)
        self.register_gui_event_handler(
            'ui_button_pressed',
            self.__start_btn,
            lambda e: self.page_manager.push(lp))
        
    def drag_handler(self, event):
        assert event.type == pygame.MOUSEBUTTONDOWN
        # click left
        if event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.__map.rect.collidepoint(mouse_pos):
                if self.tool_in_mouse:
                    # put down a tool
                    self.__map.put_tool(mouse_pos, self.tool_in_mouse)                    
                    self.tool_in_mouse = None
                else:
                    # remove tool
                    self.__map.remove_tool(mouse_pos)
            if self.__elembox.rect.collidepoint(mouse_pos):
                if not self.tool_in_mouse:
                    self.tool_in_mouse = self.__elembox.get_elem(mouse_pos)
                    self.tool_in_mouse.rect = self.tool_in_mouse.texture.get_rect()
        # click right
        if event.button == 3:
            # throw away tool in hand
            if self.tool_in_mouse:
                self.tool_in_mouse = None
                self.force_refresh = True
    def draw(self, window_surface):
        window_surface.blit(self.__background, (0, 0))
        self.__map.draw(window_surface)
        self.__elembox.draw(window_surface)
        # draw mouse
        if self.tool_in_mouse:
            self.tool_in_mouse.rect.center = pygame.mouse.get_pos()
            window_surface.blit(self.tool_in_mouse.texture,
                                self.tool_in_mouse.rect)
        self.force_refresh = False
        
class MapNamePage(pm.PageBase):
    def __init__(self):
        super().__init__(pm)
        self.__background = load_image("background/colored_forest_croped.png")
        
if __name__ == '__main__':
    pm1 = pm.PageManager((808, 700), 'hello')
    pm1.push(EditorPage(pm1, 'config/map_base.json', 'config/elem_base.json'))
    pm1.run()