'''
@author: 冯准生
@email:1565853379@qq.com
@brief:
'''

from resources.resource import load_image
from resources.resource import load_json
import surfaces
import pygame

class Elem(object):
    def __init__(self, attr: dict):   
        self.__name = attr['name']
        self.__count = attr['number']
        self.__mySymbel = attr['symble']
        self.__texture = load_image(attr['texture'])
    
    def getSymbel(self):
        return self.__mySymbel
    
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
        self.__static_surf = pygame.Surface(self.surface_size, pygame.SRCALPHA, 32)
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
        self.__map = data['map']
        
    def get_ElemMap(self):
        elem_map = [['' for _ in range(self.__size[0])]
                               for _ in range(self.__size[1])]
        
        for i in range(self.__size[1]):
            for j in range(self.__size[0]):
                if self.__tools_on_map[i][j] == None:
                    elem_map[i][j] = '.'
                elif self.__tools_on_map[i][j].getSymbel() == 'H':
                    elem_map[i][j] = '.'
                elif self.__tools_on_map[i][j].getSymbel() == 'D':
                    elem_map[i][j] = '.'
                elif self.__tools_on_map[i][j].getSymbel() == 'P':
                    elem_map[i][j] = '.'
                else:
                    elem_map[i][j] = self.__tools_on_map[i][j].getSymbel()
        return elem_map
    
    def get_CharacterPos(self):
        characters = []
        hero_pos = []
        dragon_pos = []
        princess_pos = []
        for i in range(self.__size[1]):
            for j in range(self.__size[0]):
                if self.__tools_on_map[i][j] == None:
                    continue
                if self.__tools_on_map[i][j].getSymbel() == 'H' :
                     hero_pos = [j,i]
                elif self.__tools_on_map[i][j].getSymbel() == 'D':
                    dragon_pos = [j,i]
                elif self.__tools_on_map[i][j].getSymbel() == 'P':
                    princess_pos = [j,i]

        characters.append(hero_pos)
        characters.append(dragon_pos)
        characters.append(princess_pos)
        return characters
    
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

    def draw(self, surface: pygame.Surface):
        map_surf = self.__static_surf.copy()
        # draw tools
        for i, row in enumerate(self.__tools_on_map):
            for j, tool in enumerate(row):
                if tool:
                    position = (j*self.__tile_size[0], i*self.__tile_size[1])
                    map_surf.blit(tool.texture, position)
        surface.blit(map_surf,self.__rect)


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
