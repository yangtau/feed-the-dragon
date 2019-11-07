'''
@author: yangtau
@email: yanggtau@gmail.com
@brief:
    The controller of the game
'''
import pygame
from queue import Queue
import itertools
from game_map import MapSurface


class Contoller(object):
    def __init__(self, map_surf: MapSurface, roles: dict):
        # state
        # 0: inactive (not start)
        # 1: active (not end)
        # 1: succeed
        # 2: fail
        self.__state = 0
        self.__is_block = map_surf.is_block
        self.__get_tool_name = map_surf.get_tool_name
        self.__hero = roles['hero']
        # role: game_page.Role
        self.__princess = roles['princess']
        self.__dragon = roles['dragon']
        self.__map_size = map_surf.map_size

    @property
    def state(self):
        '''Return state of the current game'''
        if self.__state == 0:
            return 'inactive'
        if self.__state == 1:
            return 'active'
        elif self.__state == 2:
            return 'succeed'
        else:
            return 'fail'

    def reset_state(self):
        self.__state = 0
        self.__hero.reset()

    def state_check(self):
        if self.__state == 1:
            if self.__hero.collide(self.__dragon):
                self.__state = 2
                print('succeed')
                self.__hero.clear_actions()
                self.__hero.add_action('fall_down')
            if self.__hero.collide(self.__princess):
                print('fail')

    def __state_trans(self, state, visited):
        res = []
        x, y = state
        # Case 1: walk right
        if not self.__is_block((x+1, y)) and self.__is_block((x+1, y+1)):
            res.append(('walk', (x+1, y)))
        # left
        if not self.__is_block((x-1, y)) and self.__is_block((x-1, y+1)):
            res.append(('walk', (x-1, y)))
        # Case 2: jump
        for i in range(y, 0, -1):
            # top of current cell should be empty
            if self.__is_block((x, i-1)):
                break
            # top of the block that hero jump to, should be empty
            if self.__is_block((x+1, i)) and not self.__is_block((x+1, i-1)):
                res.append(('jump', (x+1, i-1)))
            if self.__is_block((x-1, i)) and not self.__is_block((x-1, i-1)):
                res.append(('jump', (x-1, i-1)))
        # Case 3: fall
        for i in range(y, self.__map_size[1]-1):
            if not self.__is_block((x+1, i)) and \
                    not self.__is_block((x+1, i+1)) and self.__is_block((x+1, i+2)):
                res.append(('fall', (x+1, i+1)))
            if not self.__is_block((x-1, i)) and \
                    not self.__is_block((x-1, i+1)) and self.__is_block((x-1, i+2)):
                res.append(('fall', (x-1, i+1)))

        return [(f, pos) for f, pos in res if pos not in visited]

    def find_the_way(self):
        '''find the way that the hero should go'''
        start = self.__hero.init_pos
        end = self.__princess.init_pos
        que = Queue()
        visited = set()
        que.put((None, start, None))
        visited.add(start)
        while not que.empty():
            front = que.get()
            if front[1] == end:
                res = front
                break
            tra = self.__state_trans(front[1], visited)
            # print(tra)
            for f, pos in tra:
                que.put((f, pos, front))
                visited.add(pos)
        else:
            raise Exception('No solution found. The map is not a valid one.')
        actions = []

        def decode_res(res):
            f, p, pre = res
            if pre:
                decode_res(pre)
            actions.append((f, p))
        decode_res(res)
        return actions

    def start(self):
        actions = self.find_the_way()
        print(actions)

        def get_tool_name(x, y):
            return self.__get_tool_name((x, y))

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
            # print(res)
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
            # print(f, paths)
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
                self.__hero.add_action(f, p)
            if f != 'walk' and f is not None:
                self.__hero.add_action(f, p)
        self.__state = 1
