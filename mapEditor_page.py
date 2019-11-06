# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 09:17:12 2019
@file:  mapEditor_page.py
@brief: this file is a page which maneges the map_editor

@author: 冯准生
@email:1565853379@qq.com
"""

import json
import pygame
import pygame_gui
import page_manager as pm
from resources.resource import load_image,get_font

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
        btn_rect = pygame.Rect((700, 620),(100,60))
        self.__end_btn = pygame_gui.elements.UIButton(
            btn_rect, "完成!", self.gui_manager)

        self.register_gui_event_handler(
            'ui_button_pressed',
            self.__end_btn,
            lambda e: self.page_manager.push(MapNamePage(self.page_manager,
                        self.__map.get_ElemMap(),self.__map.get_CharacterPos())))
        
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
    size = (808, 700)
    # title
    title_y_off = 30
    title_str = '地图名称'
    title_text_size = 50
    title_color = (120, 120, 255)
    def __init__(self, pm, elem, characters):
        super().__init__(pm)
        self.__background = load_image("background/colored_forest_croped.png")
        self.register_event_handler(pygame.KEYDOWN, self.drag_handler)
        self.elem_map = elem
        self.hero_pos = characters[0]
        self.dragon_pos = characters[1]
        self.princess_pos = characters[2]
        self.__init_title()
        self.__init_inputBox()
        
    def __init_title(self):
        font = get_font('noto-sans-bold', self.title_text_size)
        text = font.render(
            self.title_str, True, self.title_color)
        self.__title_text = text
        self.__title_pos = ((self.size[0]-text.get_width())//2,
                            self.title_y_off)
    def __init_inputBox(self):
        textLine_rect = pygame.Rect((300, 100),(200, 60))
        self.__end_btn = pygame_gui.elements.UITextEntryLine(
            textLine_rect, self.gui_manager)
        
    def drag_handler(self,event):
        for event in pygame.event.get():
            if event.user_type == 'ui_text_entry_finished':
                print("Entered text:", event.text)
                self.save_map(self.elem_map, self.hero_pos, self.dragon_pos, self.princess_pos, event.text)
    
    def draw(self, window_surface):
        window_surface.blit(self.__background, (0, 0))
        window_surface.blit(self.__title_text, self.__title_pos)
        
    def save_map(self,elem_map, hero_pos, dragon_pos, princess_pos, map_name):
        map_now = {}
        map_now['size'] = [12,9]
        map_now['tile_size'] = [64,64]
        map_now['background'] = "background/colored_forest_croped.png"
        map_now['map'] = elem_map
        map_now['tiles'] = {
                "^": {
                      "name": "grass",
                      "texture": "tiles/grassMid.png"
                     },
                ".": {
                      "name": "blank"
                     },
                "$": {
                      "name": "rock",
                      "texture": "tiles/grassCenter.png"
                     },
                "w": {
                      "name": "wall",
                      "texture": "tiles/castleCenter.png"
                     }
                }
        map_now['sprites'] ={
                "hero":{
                        "position":hero_pos,
                        "json": "hero/character.json"
                        },
                "dragon":{
                        "position":dragon_pos,
                        "json": "zombie/character.json"
                        },
                "princess":{
                        "position":princess_pos,
                        "json": "princess/character.json"
                        }
                }

        filepath = 'D:\\gitRepository\\feedDragon_python\\feed-the-dragon\\resources\\config\\%s.json'%map_name
        with open(filepath,'w') as f:
            json.dump(map_now,f)
    
        
if __name__ == '__main__':
    pm1 = pm.PageManager((808, 700), 'hello')
    pm1.push(EditorPage(pm1, 'config/map_base.json', 'config/elem_base.json'))
    pm1.run()