import pygame
import configparser
import os


def load_image(filename):
    res_dir = './resources'
    filepath = os.path.join(res_dir, filename)
    return pygame.image.load(filepath).convert_alpha()


class Surface(object):
    def __init__(self):
        pass

    def get_size(self):
        pass

    def get_is_updated(self):
        pass

    def get_surface(self):
        pass


class Map(Surface):
    def __init__(self, filename: str):
        self.tiles = {}
        self.map = []
        self.tile_size = 70
        self.load_map_file(filename)
        self.__surface = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        self.__updated = True
        self.render()

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
        surface = self.__surface
        # draw background
        size = self.background.get_size()
        surface.blit(self.background, (0, self.size[1]-size[1]))
        print(size)
        for i, row in enumerate(self.map):
            for j, c in enumerate(row):
                if self.tiles[c]:
                    pos = (j*self.tile_size, i*self.tile_size)
                    if 'texture' in self.tiles[c]:
                        texture = self.tiles[c]['texture']
                        surface.blit(texture, pos)
        self.__surface = surface.convert_alpha()

    def get_surface(self):
        self.__updated = False
        return self.__surface

    def get_size(self):
        return self.size

    def get_is_updated(self):
        return self.__updated


class Toolbox(Surface):
    def __init__(self, filename: str):
        self.__updated = True
        self.tiles = {}
        self.tile_size = 50
        self.load_toolbox_file(filename)
        self.__surface = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        self.render()

    def get_is_updated(self):
        return self.__updated

    def get_size(self):
        return self.size

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

    def render(self):
        surface = self.__surface
        for i, c in enumerate(self.tools):
            if self.tiles[c]:
                pos = (i*self.tile_size, 0)
                if 'texture' in self.tiles[c]:
                    print(c)
                    texture = self.tiles[c]['texture']
                    surface.blit(texture, pos)
        self.__surface = surface.convert_alpha()

    def get_surface(self):
        self.__updated = False
        return self.__surface
