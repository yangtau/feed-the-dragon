from resources.resource import load_image
import pygame


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
        self.__surface = pygame.Surface(self.__surf_size, pygame.SRCALPHA, 32)
        self.__render()

    def __render(self):
        for i, row in enumerate(self.__map):
            for j, tile in enumerate(row):
                pos = (j*self.__tile_size[0], i*self.__tile_size[1])
                if tile.is_block:
                    self.__surface.blit(tile.texture, pos)

    def __load_config(self, config: dict):
        self.__map = []
        # tiles
        tiles = config['tiles']
        for k, v in tiles.items():
            tiles[k] = Tile(v)
        # map
        for row in config['map']:
            self.__map.append([tiles[c] for c in row])
        # surface_size
        tile_size = tuple(config['tile_size'])
        self.__tile_size = tile_size
        self.__surf_size = (tile_size[0] * len(self.__map[0]),
                            tile_size[1] * len(self.__map))

    def is_block(self, idx_pos: (int, int)) -> bool:
        return self.__map[idx_pos[1]][idx_pos[0]].is_block

    @property
    def surface(self):
        return self.__surface
