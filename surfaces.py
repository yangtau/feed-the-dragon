import pygame
import sprite
from resources.resource import load_image
from resources.resource import load_json


class Tile(object):
    '''Tile
    Attr:
        texture
        is_block
    '''

    def __init__(self, attr: dict):
        # Note: only if the name field in config file is `blank`,
        #       the tile is not a block.
        self.__is_block = attr['name'] != 'blank'
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
    '''Tool
    Attr:
        texture
        name
    Method:
        inc_count
        dec_count
    '''

    def __init__(self, attr: dict):
        self.__texture = load_image(attr['texture'])
        self.__name = attr['name']
        self.__count = attr['number']

    @property
    def texture(self):
        return self.__texture

    @property
    def name(self):
        return self.__name

    def inc_count(self):
        self.__count += 1

    def dec_count(self):
        self.__count -= 1


class Surface(object):
    def __init__(self):
        pass

    def get_relative_position(self, position):
        return (position[0] - self.rect.left, position[1] - self.rect.top)


class Map(Surface):
    '''Map
    attr:
        __map: two-dimensional list of tiles
        __static_surf: background and tiles. Copy it before drawing.
        __tools_on_map: two-dimensional list of tools in the map
        __size: the scale of __map
        __background: pygame image of background
        __tile_size: size of tile
        __hero:
        __dragon:
        __hero_position:
        __dragon_position:
    mothed:
        __load_config: load json configuration file
        __render_static: render background and tiles
        draw:
    '''

    def __init__(self, config: str, position: (int, int)):
        self.__map = []
        self.__load_config(config)
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

    def __load_config(self, config: str):
        data = load_json(config)
        self.__size = tuple(data['size'])
        self.__tile_size = tuple(data['tile_size'])
        self.__background = load_image(data['background'])
        # tiles
        tiles = data['tiles']
        for k, v in tiles.items():
            tiles[k] = Tile(v)
        for row in data['map']:
            self.__map.append([tiles[c] for c in row])
        # hero
        self.__hero_position = tuple(data['hero']['position'])
        self.__hero = sprite.Hero(data['hero']['json'], self.__hero_position)
        # dragon
        self.__dragon_position = tuple(data['dragon']['position'])
        self.__dragon = sprite.Dragon(
            data['dragon']['json'], self.__dragon_position)

    def put_tool(self, position: (int, int), tool: Tool):
        '''Put the tool in the position
        '''
        relative_pos = self.get_relative_position(position)
        idx_x = (relative_pos[0])//self.__tile_size[0]
        idx_y = (relative_pos[1])//self.__tile_size[1]
        self.__tools_on_map[idx_y][idx_x] = tool

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
        # draw tiles
        for i, row in enumerate(self.__map):
            for j, tile in enumerate(row):
                position = (j*self.__tile_size[0], i*self.__tile_size[1])
                if tile.is_block:
                    surface.blit(tile.texture, position)
        return surface

    def draw(self, surface: pygame.Surface):
        map_surf = self.__static_surf.copy()
        # draw tools
        for i, row in enumerate(self.__tools_on_map):
            for j, tool in enumerate(row):
                if tool:
                    position = (j*self.__tile_size[0], i*self.__tile_size[1])
                    map_surf.blit(tool.texture, position)
        # draw hero and dragon
        '''
        self.__hero.draw(map_surf)
        self.__dragon.draw(map_surf)
        '''
        surface.blit(map_surf, self.__rect)

    def go_hero(self):
        '''a bad mothed name'''
        pass


class Toolbox(Surface):
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
        self.__number = data['number']
        self.__tool_size = tuple(data['tool_size'])
        tools = data['tools']
        for k, v in tools.items():
            tools[k] = Tool(v)
        self.__toolbox = [tools[c] for c in data['toolbox']]

    def get_tool(self, position: (int, int)) -> Tool:
        '''return the tool in the position
        '''
        relative_pos = self.get_relative_position(position)
        idx = relative_pos[0] // self.__tool_size[0]
        return self.__toolbox[idx]

    @property
    def surface_size(self):
        return (self.__tool_size[0] * self.__number, self.__tool_size[1])

    def __render__static(self):
        surface = pygame.Surface(self.surface_size, pygame.SRCALPHA, 32)
        for i, tool in enumerate(self.__toolbox):
            surface.blit(tool.texture, (i * self.__tool_size[0], 0))
        return surface.convert_alpha()

    def draw(self, surface: pygame.Surface):
        surface.blit(self.__static_surf, self.__rect)
