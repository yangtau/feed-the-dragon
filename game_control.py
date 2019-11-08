'''
@author: yangtau
@email: yanggtau+fd@gmail.com
@brief:
    The controller of the game
TODO:
    1.the effect between two tools.
    2.state detect by the path the hero pass.
    3.open fail_page or succeed_page when the game ends.
'''
import pygame
from queue import Queue
import itertools
from game_map import MapSurface


class Contoller(object):
    def __init__(self, map_surf: MapSurface, roles: dict,
                 success_handler, fail_handler):
        # state
        # 0: inactive (not start)
        # 1: active (not end)
        self.__state = 0
        self.__is_block = map_surf.is_block
        self.__get_tool_name = map_surf.get_tool_name
        self.__hero = roles['hero']
        # role: game_page.Role
        self.__princess = roles['princess']
        self.__dragon = roles['dragon']
        self.__map_size = map_surf.map_size
        # fail and success handler
        self.__success_handler = success_handler
        self.__fail_handler = fail_handler

    @property
    def state(self):
        '''Return state of the current game'''
        if self.__state == 0:
            return 'inactive'
        if self.__state == 1:
            return 'active'
        else:
            return 'end'

    def reset_state(self):
        self.__state = 0
        self.__hero.reset()

    def state_check(self):
        if self.__state == 1:
            if self.__hero.collide(self.__dragon):
                self.__state = 2
                self.__hero.clear_actions()
                self.__hero.add_action(
                    'fall_down', action_event=self.__success_handler)
            if self.__hero.collide(self.__princess):
                self.__state = 2
                self.__hero.clear_actions()
                self.__hero.add_action(
                    'cheer', action_event=self.__fail_handler)
                self.__princess.add_action(
                    'cheer', action_event=self.__fail_handler)

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
            for f, pos in tra:
                que.put((f, pos, front))
                visited.add(pos)
        else:
            raise Exception('No solution found. The map is not a valid one.')
        actions = []
        pre = res
        while pre is not None:
            f, p, pre = pre
            actions.append((f, p))
        actions.reverse()
        return actions

    def add_flights(self, actions):
        def get_direction(position):
            #   0
            #  2 3
            #   1
            x, y = position
            directions = [self.__get_tool_name(pos) for pos in
                          [(x, y-1), (x, y+1), (x-1, y), (x+1, y)]]
            dire = None
            if directions[0] == 'down' and directions[1] != 'up':
                dire = 'down'
            elif directions[0] != 'down' and directions[1] == 'up':
                dire = 'up'
            elif directions[2] == 'right' and directions[3] != 'left':
                dire = 'right'
            elif directions[2] != 'right' and directions[3] == 'left':
                dire = 'left'
            return dire
        # detect tools in the way
        for i in range(len(actions)):
            f, (idx_x, idx_y) = actions[i]
            # flatter the path of jump and fall
            paths = []
            if f == 'jump':
                _, (px, py) = actions[i-1]
                paths.extend(zip(itertools.repeat(px),
                                 range(py, idx_y-1, -1)))
                paths.append((idx_x, idx_y))
            elif f == 'fall':
                _, (_, py) = actions[i-1]
                paths.extend(zip(itertools.repeat(idx_x),
                                 range(py, idx_y+1, 1)))
            else:
                paths.append((idx_x, idx_y))
            for x, y in paths:
                dire = get_direction((x, y))
                if dire is None:
                    continue
                flights = [((x, y), dire)]
                while True:
                    (idx_x, idx_y) = flights[-1][0]
                    dire = get_direction((idx_x, idx_y))
                    last = False
                    if dire is None:
                        dire = flights[-1][1]
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
                        flights[-1] = ((idx_x, idx_y), dire)
                    else:
                        flights.append(((idx_x, idx_y), dire))
                actions[i] = (f, (x, y))
                actions = actions[:i+1] + [('fly', pos) for pos, _ in flights]
                actions.append(('fall_down', (idx_x, 10)))
                return actions
        return actions

    def start(self):
        actions = self.find_the_way()
        actions = self.add_flights(actions)
        actions.append((None, None))
        for i in range(1, len(actions)):
            f, p = actions[i-1]
            if f == 'fall_down':
                self.__hero.add_action(f, p, self.__fail_handler)
                continue
            if f == 'walk' and actions[i][0] != 'walk':
                self.__hero.add_action(f, p)
            if f != 'walk' and f is not None:
                self.__hero.add_action(f, p)
        self.__state = 1
