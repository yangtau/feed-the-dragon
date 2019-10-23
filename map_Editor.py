# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 20:01:31 2019
@file:
@brief:

@author: 冯准生
@email:1565853379@qq.com
"""

from resources.resource import load_image
from resources.resource import load_json
from collections import defaultdict
import surfaces
import pygame
import json

class Elem(object):
    def __init__(self, attr: dict):
        self.__texture = load_image(attr['texture'])
        self.__name = attr['name']
        self.__count = attr['number']
        self.__symble = attr['symble']
    
    def __getSymble(self):
        return self.__symble
    
    @property
    def texture(self):
        return self.__texture

    @property
    def name(self) -> str:
        return self.__name

    def inc_count(self):
        self.__count += 1

    def dec_count(self):
        self.__count -= 1

class Map_base(surfaces.Surface):
    def __init__(self, config: str, position: (int, int)):
        self.__map = []
        self.load_config(config)
        self.__tools_on_map = [[None for _ in range(self.__size[0])]
                               for _ in range(self.__size[1])]
        # static_surf will never change
        self.__static_surf = self.__render_static()
        self.__rect = self.__static_surf.get_rect()
        self.__rect.move_ip(position)
        
    @property
    def rect(self) -> pygame.Rect:
        return self.__rect

    @property
    def surface_size(self):
        return (self.__size[0] * self.__tile_size[0],
                self.__size[1] * self.__tile_size[1])    
    
    def load_config(self, config: str):
        data = load_json(config)
        self.__size = tuple(data['size'])
        self.__tile_size = tuple(data['tile_size'])
        self.__background = load_image(data['background'])
        self.__map = data['map']
        
    def __get_ElemMap(self):
        elem_map = [['' for _ in range(self.__size[0])]
                               for _ in range(self.__size[1])]
        for i in range(self.__size[0]):
            for j in range(self.__size[1]):
                if self.__tools_on_map[i][j] == None:
                    elem_map[i][j] = '.'
                elif self.__tools_on_map[i][j].__getSymbel() == 'H':
                    elem_map[i][j] = '.'
                elif self.__tools_on_map[i][j].__getSymbel() == 'D':
                    elem_map[i][j] = '.'    
                else:
                    elem_map[i][j] = self.__tools_on_map[i][j].__getSymbel()
        return elem_map
    
    def __get_CharacterPos(self):
        hero_pos = []
        dragon_pos = []
        for i in range(self.__size[0]):
            for j in range(self.__size[1]):
                if self.__tools_on_map[i][j].__getSymble() == 'H' :
                    hero_pos = [i,j]
                elif self.__tools_on_map[i][j].__getSymble() == 'D':
                    dragon_pos = [i,j]
        return hero_pos,dragon_pos
    
    def put_tool(self, position: (int, int), elem : Elem):
        '''Put the tool in the position
        '''
        relative_pos = self.get_relative_position(position)
        idx_x = (relative_pos[0])//self.__tile_size[0]
        idx_y = (relative_pos[1])//self.__tile_size[1]
        self.__tools_on_map[idx_y][idx_x] = elem


    def remove_tool(self, position: (int, int)):
        relative_pos = self.get_relative_position(position)
        idx_x = (relative_pos[0])//self.__tile_size[0]
        idx_y = (relative_pos[1])//self.__tile_size[1]
        self.__tools_on_map[idx_y][idx_x] = None

    def __render_static(self):
        surface = pygame.Surface(self.surface_size, pygame.SRCALPHA, 32)
        # draw background
        background_size = self.__background.get_size()
        surface.blit(self.__background,
                     (0, self.surface_size[1]-background_size[1]))
        
        return surface

    def draw(self, surface: pygame.Surface):
        map_surf = self.__static_surf.copy()
        # draw tools
        for i, row in enumerate(self.__tools_on_map):
            for j, tool in enumerate(row):
                if tool:
                    position = (j*self.__tile_size[0], i*self.__tile_size[1])
                    map_surf.blit(tool.texture, position)
        surface.blit(map_surf, self.__rect)


class Elem_base(surfaces.Surface):
    def __init__(self, config: str, position: (int, int)):
        self.__load_config(config)
        self.__static_surf = self.__render__static()
        self.__rect = self.__static_surf.get_rect()
        self.__rect.move_ip(position)

    @property
    def rect(self) -> pygame.Rect:
        return self.__rect
    
    def __load_config(self, config: str):
        data = load_json(config)
        self.__number = data['elem_number']
        self.__elem_size = tuple(data['elem_size'])
        elem = data['elem']
        for k, v in elem.items():
            elem[k] = Elem(v)
        self.__elembox = [elem[c] for c in data['elem_name']]
    
    def get_elem(self, position: (int, int)) -> Elem:
        '''return the tool in the position
        '''
        relative_pos = self.get_relative_position(position)
        idx = relative_pos[0] // self.__elem_size[0]
        return self.__elembox[idx]

    @property
    def surface_size(self):
        return (self.__elem_size[0] * self.__number, self.__elem_size[1])

    def __render__static(self):
        surface = pygame.Surface(self.surface_size, pygame.SRCALPHA, 32)
        for i, elem in enumerate(self.__elembox):
            surface.blit(elem.texture, (i * self.__elem_size[0], 0))
        return surface.convert_alpha()

    def draw(self, surface: pygame.Surface):      
        surface.blit(self.__static_surf, self.__rect)

class Map_editer():
    def __init__(self, title: str, size: (int, int), fps=60):
        self.__elme_map = []
        self.__hero_pos = []
        self.__dragon_pos = []
        self.title = title
        self.size = size
        self.fps = fps
        self.surface = None
        self.clock = None
        self.tool_in_mouse = None
        self.force_refresh = False
        self.__event_handlers = defaultdict(list)
        self.__event_handlers[pygame.MOUSEBUTTONDOWN].append(self.drag_handler)
        self.__init_pygame()

    def set_map(self, m: Map_base):
        self.__map = m

    def set_elembox(self, elembox: Elem_base):
        self.__elembox = elembox

    def enroll_event_handler(self,
                             event: int,
                             handler: callable):
        '''enroll event handler
        Args:
            event: pygame.event.EventType.type, event type identifier
            handler: a function taking an event as argurment
        '''
        self.__event_handlers[event].append(handler)

    def drag_handler(self, event):
        assert event.type == pygame.MOUSEBUTTONDOWN
        # click left
        if event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.__map.rect.collidepoint(mouse_pos):
                if self.tool_in_mouse:
                    # put down a tool
                    # TODO: what if there is already a tool in the mouse_pos
                    self.__map.put_tool(mouse_pos, self.tool_in_mouse)
                    # if hero or dragon, save their position
                    
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

    def run(self):
        '''start the game'''
        # draw background
        self.surface.fill((255, 255, 255))
        while True:
            self.clock.tick(self.fps)
            self.__event_handle()
            if self.tool_in_mouse or self.force_refresh:
                self.surface.fill((255, 255, 255))
            # TODO: position
            self.__map.draw(self.surface)
            self.__elembox.draw(self.surface)
            # draw mouse
            if self.tool_in_mouse:
                self.tool_in_mouse.rect.center = pygame.mouse.get_pos()
                self.surface.blit(self.tool_in_mouse.texture,
                                  self.tool_in_mouse.rect)
            pygame.display.flip()
            self.force_refresh = False
            
            # TODO: if complete to edit the map,save map and exit
            # if conditon:
            #    self.__elme_map = __map.__get_ElemMap()
            #    self.__hero_pos,self.__dragon_pos = __map.__get_CharacterPos()
            # self.save_map(self.__elme_map,self.__hero_pos,self.__dragon_pos)
            
    def save_map(self,elem_map,hero_pos,dragon_pos):
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
        map_now['hero'] = {
                "position":hero_pos,
                "json": "hero/character.json"
                }
        map_now['dragon'] = {
                "position":dragon_pos,
                "json": "zombie/character.json"
                }
        filepath = 'D:\\gitRepository\\feedDragon_python\\feed-the-dragon\\resources\\config\\map_k.json'
        with open(filepath,'w') as f:
            json.dump(map_now,f)

    def __init_pygame(self):
        pygame.init()
        pygame.display.set_caption(self.title)
        self.surface = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()

    def __event_handle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            for handler in self.__event_handlers[event.type]:
                handler(event)

if __name__ == '__main__':
    size = (808, 700)
    game = Map_editer('Feed the Dragon', size, 30)
    m = Map_base('config/map_0.json', (20, 20))
    game.set_map(m)
    elembox = Elem_base('config/elem.json', (20, 616))
    game.set_elembox(elembox)
    game.run()