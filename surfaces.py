'''
@author: yangtau
@email: yanggtau+fd@gmail.com
@breif:
    map and toolbox
'''
import pygame
from queue import Queue
import itertools
import sprites
from resources.resource import load_image
from resources.resource import load_json


'''
+-----> X
|
|
|
V Y

index_position, position: (X, Y)
    index_position: the index of the block in the map
    position: the relative position represented in pixel in the map

size, pixel_size
'''


def pair_mul(a, b):
    return (a[0] * b[0], a[1] * b[1])


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
    def name(self) -> str:
        return self.__name

    def inc_count(self):
        self.__count += 1

    def dec_count(self):
        self.__count -= 1


class Surface(object):
    def __init__(self):
        self.rect = None
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
    mothed:
        __load_config: load json configuration file
        __render_static: render background and tiles
        draw:
    '''

    def __init__(self, config: str, position: (int, int)):
        self.__map = []
        self.__group = pygame.sprite.Group()
        self.__load_config(config)
        self.__tools_on_map = [[None for _ in range(self.__size[0])]
                               for _ in range(self.__size[1])]
        # static_surf will never change
        self.__static_surf = self.__render_static()
        self.__rect = self.__static_surf.get_rect()
        self.__rect.move_ip(position)

        # state
        self.__state = 0
        # self.__state = 1  # succeed
        # self.__state = 2  # fail

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
        # TODO: abstract
        # roles
        roles = data['sprites']
        # hero
        self.__hero_idx_pos = tuple(roles['hero']['position'])
        self.__hero_position = pair_mul(self.__hero_idx_pos, self.__tile_size)
        self.__hero = sprites.Hero(
            self.__hero_position, roles['hero']['json'])
        # dragon
        self.__dragon_idx_pos = tuple(roles['dragon']['position'])
        self.__dragon_position = pair_mul(
            self.__dragon_idx_pos, self.__tile_size)
        self.__dragon = sprites.Dragon(
            self.__dragon_position, roles['dragon']['json'])
        # princess
        self.__princess_idx_pos = tuple(roles['princess']['position'])
        self.__princess_position = pair_mul(
            self.__princess_idx_pos, self.__tile_size)
        self.__princess = sprites.Princess(
            self.__princess_position, roles['princess']['json'])
        self.__group.add(self.__hero)
        self.__group.add(self.__princess)
        self.__group.add(self.__dragon)

    def __position_to_idx(self, pos: (int, int)):
        idx_x = (pos[0])//self.__tile_size[0]
        idx_y = (pos[1])//self.__tile_size[1]
        return idx_x, idx_y

    def __is_block(self, idx_pos: (int, int)):
        '''Return true if there is a block or the idx_pos is out of the map'''
        idx_x, idx_y = idx_pos
        if idx_x < 0 or idx_y < 0 or \
                idx_x >= self.__size[0] or idx_y >= self.__size[1]:
            return True
        return self.__map[idx_y][idx_x].is_block \
            or self.__tools_on_map[idx_y][idx_x] != None

    def put_tool(self, position: (int, int), tool: Tool):
        '''Put the tool in the given position'''
        relative_pos = self.get_relative_position(position)
        idx_x, idx_y = self.__position_to_idx(relative_pos)
        self.__tools_on_map[idx_y][idx_x] = tool

    def remove_tool(self, position: (int, int)):
        relative_pos = self.get_relative_position(position)
        idx_x, idx_y = self.__position_to_idx(relative_pos)
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
        self.__group.draw(map_surf)
        self.__group.update()
        self.success_check()
        surface.blit(map_surf, self.__rect)

    def reset(self):
        self.__state = 0
        self.__hero.clear_actions()
        self.__hero.position = self.__hero_position

    def success_check(self):
        if self.__state == 0 and self.__hero.rect.colliderect(self.__dragon.rect):
            self.__state = 1
            print('succeed')
            self.__hero.clear_actions()
            x = self.__hero.position[0]
            y = self.__tile_size[1] * self.__size[1]
            self.__hero.add_action(sprites.FallDown((x, y)))

    def find_the_way(self):
        '''find the way that the hero should go'''
        start = self.__hero_idx_pos
        end = self.__princess_idx_pos
        que = Queue()
        visited = set()
        que.put((None, start, None))
        visited.add(start)
        for row in self.__map:
            for t in row:
                if t.is_block:
                    print('#', end='')
                else:
                    print('0', end='')
            print()

        def trans(state):
            res = []
            size = self.__size
            x, y = state
            # Case 1: walk
            # right
            if x+1 < size[0] and not self.__is_block((x+1, y)) and self.__is_block((x+1, y+1)):
                res.append(('walk', (x+1, y)))
            # left
            if x-1 >= 0 and not self.__is_block((x-1, y)) and self.__is_block((x-1, y+1)):
                res.append(('walk', (x-1, y)))
            # Case 2: jump
            for i in range(y, 0, -1):
                # top of current cell should be empty
                if self.__is_block((x, i-1)):
                    break
                # top of the block that hero jump to, should be empty
                if x+1 < size[0] and self.__is_block((x+1, i)) and not self.__is_block((x+1, i-1)):
                    res.append(('jump', (x+1, i-1)))
                if x-1 >= 0 and self.__is_block((x-1, i)) and not self.__is_block((x-1, i-1)):
                    res.append(('jump', (x-1, i-1)))
            # Case 3: fall
            for i in range(y, size[1]-1):
                if x+1 < size[0] and not self.__is_block((x+1, i)) and \
                        not self.__is_block((x+1, i+1)) and self.__is_block((x+1, i+2)):
                    res.append(('fall', (x+1, i+1)))
                if x-1 >= 0 and not self.__is_block((x-1, i)) and \
                        not self.__is_block((x-1, i+1)) and self.__is_block((x-1, i+2)):
                    res.append(('fall', (x-1, i+1)))

            res = [(f, pos) for f, pos in res if pos not in visited]
            return res

        while not que.empty():
            front = que.get()
            if front[1] == end:
                res = front
                break
            tra = trans(front[1])
            for f, pos in tra:
                que.put((f, pos, front))
                visited.add(pos)
        else:
            # TODO
            print("No solution found")

        actions = []

        def decode_res(res):
            f, p, pre = res
            if pre:
                decode_res(pre)
            # print((f, p))
            actions.append((f, p))
        decode_res(res)
        return actions

    def start(self):
        actions = self.find_the_way()

        def get_tool_name(x, y):
            if x < 0 or y < 0 or x >= self.__size[0] or y >= self.__size[1]:
                return None
            tool = self.__tools_on_map[y][x]
            return tool.name if tool else None

        def fn(position, direction):
            res = [(position, direction)]
            while True:
                # TODO: infinite loop
                dire = ''
                idx_x, idx_y = res[-1][0]
                last = False
                # down
                if get_tool_name(idx_x, idx_y-1) == 'down':
                    dire = 'down'
                # up
                elif get_tool_name(idx_x, idx_y+1) == 'up':
                    dire = 'up'
                # right
                elif get_tool_name(idx_x-1, idx_y) == 'right':
                    dire = 'right'
                # left
                elif get_tool_name(idx_x+1, idx_y) == 'left':
                    dire = 'left'
                else:
                    dire = res[-1][1]
                    last = True

                if dire == 'left':
                    idx_x -= 1
                elif dire == 'right':
                    idx_x += 1
                elif dire == 'up':
                    idx_y -= 1
                elif dire == 'down':
                    idx_y += 1
                if self.__is_block((idx_x, idx_y)):
                    break
                if last:
                    res[-1] = ((idx_x, idx_y), dire)
                else:
                    res.append(((idx_x, idx_y), dire))
            print(res)
            return res

        # detect tools in the way
        for i in range(len(actions)):
            f, (idx_x, idx_y) = actions[i]
            # flatter the path of jump and fall
            paths = []
            if f == 'jump':
                assert i > 0
                _, (px, py) = actions[i-1]
                paths.extend(zip(itertools.repeat(px),
                                 range(py, idx_y-1, -1)))
                paths.append((idx_x, idx_y))
            elif f == 'fall':
                assert i > 0
                _, (_, py) = actions[i-1]
                paths.extend(zip(itertools.repeat(idx_x),
                                 range(py, idx_y+1, 1)))
            else:
                paths.append((idx_x, idx_y))
            print(f, paths)
            for x, y in paths:
                dire = ''
                # down
                if get_tool_name(x, y-1) == 'down':
                    dire = 'down'
                # up
                if get_tool_name(x, y+1) == 'up':
                    dire = 'up'
                # right
                if get_tool_name(x-1, y) == 'right':
                    dire = 'right'
                # left
                if get_tool_name(x+1, y) == 'left':
                    dire = 'left'
                if dire == '':
                    continue
                flights = fn((x, y), dire)
                actions[i] = (f, (x, y))
                actions = actions[:i+1] + [('fly', pos) for pos, _ in flights]
                break
            else:
                continue
            break
        print(actions)
        actions.append((None, None))
        for i in range(1, len(actions)):
            f, p = actions[i-1]
            if f == 'walk' and actions[i][0] != 'walk':
                self.__hero.add_action(sprites.Walk(
                    pair_mul(p, self.__tile_size)))
            if f != 'walk':
                if f == 'jump':
                    self.__hero.add_action(sprites.Jump(
                        pair_mul(p, self.__tile_size)))
                elif f == 'fall':
                    self.__hero.add_action(sprites.Fall(
                        pair_mul(p, self.__tile_size)))
                elif f == 'fly':
                    self.__hero.add_action(sprites.Fly(
                        pair_mul(p, self.__tile_size)))


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
