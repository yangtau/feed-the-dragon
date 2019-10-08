import pygame
import configparser
from resources.resource import load_image


class Surface(object):
    def __init__(self):
        self.size = (0, 0)
        self.is_updated = True
        self.rect = None
        self.surface = None


# TODO: updated in only one position
#       add a tool class

class Map(Surface):
    def __init__(self, filename: str, pos: tuple):
        super().__init__()
        self.tiles = {}
        self.map = []
        self.tile_size = 70
        self.load_map_file(filename)
        self.tools_on_map = [[None for _ in range(
            len(self.map[0]))] for _ in range(len(self.map))]
        self.render()
        self.rect.move_ip(*pos)

    def get_obj_in(self, pos):
        rel_pos = (pos[0]-self.rect.left, pos[1]-self.rect.top)
        idx_x = (rel_pos[0])//self.tile_size
        idx_y = (rel_pos[1])//self.tile_size
        return self.tiles[self.map[idx_y][idx_x]]

    def put_obj_in(self, pos, tool):
        rel_pos = (pos[0]-self.rect.left, pos[1]-self.rect.top)
        idx_x = (rel_pos[0])//self.tile_size
        idx_y = (rel_pos[1])//self.tile_size
        print('put down', (idx_x, idx_y))
        self.tools_on_map[idx_y][idx_x] = tool
        # render
        self.is_updated = True
        texture = tool['texture']
        size = texture.get_size()
        offset = (self.tile_size - size[0]) // 2
        pos = (idx_x*self.tile_size+offset, idx_y*self.tile_size+offset)
        self.surface.blit(texture, pos)

    def load_map_file(self, filename: str):
        parser = configparser.ConfigParser()
        parser.read(filename)
        self.map = parser.get('map', 'map').split('\n')
        self.size = tuple(map(lambda x: int(x)*self.tile_size,
                              parser.get('map', 'size').split(' ')))
        self.background = load_image(parser.get('map', 'background-texture'))
        # tile
        for sec in parser.sections():
            if len(sec) == 1:
                des = dict(parser.items(sec))
                self.tiles[sec] = des
                if 'texture' in des:
                    des['texture'] = load_image(des['texture'])

    def render(self):
        self.is_updated = True
        surface = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        # draw background
        size = self.background.get_size()
        surface.blit(self.background, (0, self.size[1]-size[1]))
        for i, row in enumerate(self.map):
            for j, c in enumerate(row):
                if self.tiles[c]:
                    pos = (j*self.tile_size, i*self.tile_size)
                    if 'texture' in self.tiles[c]:
                        texture = self.tiles[c]['texture']
                        surface.blit(texture, pos)
        for i, row in enumerate(self.tools_on_map):
            for j, tool in enumerate(row):
                if tool:
                    pos = (j*self.tile_size, i*self.tile_size)
                    texture = tool['texture']
                    self.surface.blit(texture, pos)
        self.surface = surface.convert_alpha()
        self.rect = self.surface.get_rect()


class Toolbox(Surface):
    def __init__(self, filename: str, pos: tuple):
        super().__init__()
        self.tiles = {}
        self.tile_size = 70
        self.load_toolbox_file(filename)
        self.render()
        self.rect.move_ip(*pos)

    def load_toolbox_file(self, filename: str):
        parser = configparser.ConfigParser()
        parser.read(filename)
        self.tools = parser.get('toolbox', 'tools')
        self.size = tuple(map(lambda x: int(x)*self.tile_size,
                              parser.get('toolbox', 'size').split(' ')))
        # tiles
        for sec in parser.sections():
            if len(sec) == 1:
                des = dict(parser.items(sec))
                self.tiles[sec] = des
                if 'texture' in des:
                    des['texture'] = load_image(des['texture'])

    def get_obj_in(self, pos):
        rel_pos = (pos[0]-self.rect.left, pos[1]-self.rect.top)
        idx = (rel_pos[0])//self.tile_size
        return self.tiles[self.tools[idx]]

    def render(self):
        # TODO: init surface when create the object
        surface = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        for i, c in enumerate(self.tools):
            if self.tiles[c]:
                pos = (i*self.tile_size, 0)
                if 'texture' in self.tiles[c]:
                    texture = self.tiles[c]['texture']
                    surface.blit(texture, pos)
        self.surface = surface.convert_alpha()
        self.rect = self.surface.get_rect()
