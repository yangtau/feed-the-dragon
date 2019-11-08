'''
@author: yangtau
@email: yanggtau+fd@gmail.com
@brief:
    Map
'''
from resources.resource import load_image
import pygame
import pygame_gui


class Tile(object):
    '''Tile
    Attr:
        texture
        is_block
    '''

    def __init__(self, attr: dict):
        # Note: only if the name field in config file is `blank`,
        #       the tile is not a block.
        self.__is_block = (attr['name'] != 'blank')
        if self.__is_block:
            self.__texture = load_image(attr['texture'])
        else:
            self.__texture = None

    @property
    def texture(self):
        return self.__texture

    @property
    def is_block(self):
        return self.__is_block


class Tool(object):
    def __init__(self, tool_config: dict, btn: pygame_gui.elements.UIButton):
        self.__texture = load_image(tool_config['texture'])
        self.__name = tool_config['name']
        self.__count = tool_config['number']
        self.__btn = btn
        if self.number == 0:
            self.__btn.disable()
        self.__btn.set_text(str(self.number))

    @property
    def button(self):
        return self.__btn

    @property
    def texture(self):
        return self.__texture

    @property
    def number(self):
        return self.__count

    @property
    def name(self) -> str:
        return self.__name

    def inc_num(self):
        self.__count += 1
        if self.number > 0:
            self.__btn.enable()
        self.__btn.set_text(str(self.number))

    def dec_num(self):
        self.__count -= 1
        if self.number == 0:
            self.__btn.disable()
        self.__btn.set_text(str(self.number))


class MapSurface(object):
    def __init__(self, config: dict):
        '''
        :param config: {
            "tile_size": []
            "map": [""],
            "tiles": [{".":{"name":"", "texture":""}}...]
        }
        '''
        self.__load_config(config)
        self.__surface = None
        self.__redraw()

    def __redraw(self):
        w, h = self.__tile_size
        self.__surface = pygame.Surface(self.__surf_size, pygame.SRCALPHA, 32)
        # tiles
        for i, row in enumerate(self.__map):
            for j, tile in enumerate(row):
                if tile.is_block:
                    self.__surface.blit(tile.texture, (j*w, i*h))
        # tools
        for i, row in enumerate(self.__tool_on_map):
            for j, tool in enumerate(row):
                if tool is not None:
                    self.__surface.blit(tool.texture, (j*w, i*h))

    def __update_tool(self, idx_pos):
        '''Append a new tool on the original surface'''
        x, y = idx_pos
        w, h = self.__tile_size
        tool = self.__tool_on_map[y][x]
        self.__surface.blit(tool.texture, (x*w, y*h))

    def __load_config(self, config: dict):
        self.__map = []
        # tiles
        w, h = tuple(config['tile_size'])
        self.__tile_size = (w, h)
        tiles = dict()
        for k, v in config['tiles'].items():
            tiles[k] = Tile(v)
        # map
        for row in config['map']:
            self.__map.append([tiles[c] for c in row])
        row, col = len(self.__map[0]), len(self.__map)
        self.__map_size = row, col
        self.__surf_size = row*w, col*h
        # tools on map
        self.__tool_on_map = [[None for _ in range(row)] for _ in range(col)]

    def is_block(self, idx_pos: (int, int)) -> bool:
        '''Return true if there is a block or a tool, or the position 
           is out of map.
        '''
        x, y = idx_pos
        xl, yl = self.__map_size
        if x < 0 or y < 0 or x >= xl or y >= yl:
            return True
        return self.__map[y][x].is_block \
            or self.__tool_on_map[y][x] != None

    def get_tool_name(self, idx_pos: (int, int)):
        x, y = idx_pos
        xl, yl = self.__map_size
        if x < 0 or y < 0 or x >= xl or y >= yl or\
                self.__tool_on_map[y][x] is None:
            return None
        return self.__tool_on_map[y][x].name

    @property
    def map_size(self):
        return self.__map_size

    def position_to_index(self, pos: (int, int)) -> (int, int):
        w, h = self.__tile_size
        return pos[0]//w, pos[1]//h

    def put_tool(self, tool, position: (int, int)) -> bool:
        '''Return true if the tool is put successfully
        :param tool: Tool
        :param position: The relative position with respect to map.
        '''
        idx_x, idx_y = self.position_to_index(position)
        if self.__tool_on_map[idx_y][idx_x] is not None:
            return False  # there is already a tool in the position
        self.__tool_on_map[idx_y][idx_x] = tool
        self.__update_tool((idx_x, idx_y))
        return True

    def remove_tool(self, position: (int, int)) -> Tool:
        '''Return the tool int the position and remove it from the map'''
        idx_x, idx_y = self.position_to_index(position)
        if self.__tool_on_map[idx_y][idx_x] is None:
            return None
        tool = self.__tool_on_map[idx_y][idx_x]
        self.__tool_on_map[idx_y][idx_x] = None
        self.__redraw()
        return tool

    @property
    def surface(self):
        return self.__surface
