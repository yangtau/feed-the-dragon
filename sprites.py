import pygame
import math
from queue import Queue
from collections import defaultdict
from resources.resource import load_image
from resources.resource import load_json


class Action(object):
    def __init__(self, to_pos: (int, int)):
        self.__to_pos = to_pos
        self.__position = None

    @property
    def pose(self) -> str:
        pass

    @property
    def to_pos(self) -> (int, int):
        return self.__to_pos

    @property
    def position(self) -> (int, int):
        return self.__position

    @position.setter
    def position(self, pos: (int, int)):
        self.__position = pos

    def arrived(self) -> bool:
        return self.position == self.to_pos

    def update(self):
        '''update the position'''
        pass

    def __str__(self):
        return '"%s" %s' % (self.pose, self.to_pos)

    @classmethod
    def get_new_position(cls, _from: int, _to: int, speed):
        if _to < _from:
            return _from - min(speed, _from - _to)
        else:
            return _from + min(speed, _to - _from)


class Idle(Action):
    def __init__(self):
        self.position = None

    def arrived(self):
        return True

    @property
    def to_pos(self):
        return self.position

    @property
    def pose(self):
        return 'idle'

    def update(self):
        pass


class Walk(Action):
    speed = 2
    @property
    def pose(self):
        return 'walk'

    def update(self):
        self.position = (self.get_new_position(self.position[0], self.to_pos[0], self.speed),
                         self.get_new_position(self.position[1], self.to_pos[1], self.speed))


class Jump(Action):
    '''
    Attr:
        state: 0 not active
               1 rise
               2 fall and linearly move
               3 linearly move
    '''
    g = 0.3  # gravitational acceleration
    speed = 2  # speed of linearly moving

    def __init__(self, to_pos: (int, int)):
        super().__init__(to_pos)
        self.__state = 0

    @property
    def pose(self):
        if self.__state == 1:
            return 'jump'
        elif self.__state == 2:
            return 'fall'
        elif self.__state == 3:
            return 'walk'
        else:
            return 'idle'

    def update(self):
        x, y = self.position
        if self.__state == 0:
            self.__state = 1
            # - 24 means that the top position of the action is
            # 24 piexl higher than the to_pos.
            self.__top_point = self.to_pos[1] - 24
            # sum(V0, V1, ..., Vn) = h, V_n = V_{n-1} - a
            self.__v = math.sqrt(2 * self.g * (y - self.__top_point))
        elif self.__state == 1:
            # y = int(y - min(self.__v, y - self.__top_point))
            y = int(self.get_new_position(y, self.__top_point, self.__v)+0.5)
            self.__v -= self.g
            # assert self.__v > 0
            self.position = (x, y)
            if y == self.__top_point:
                self.__state = 2
                self.__v = 0
        elif self.__state == 2:
            # y = int(y + min(self.__v, self.to_pos[1] - y))
            y = int(self.get_new_position(y, self.to_pos[1], self.__v)+0.5)
            x = self.get_new_position(x, self.to_pos[0], self.speed)
            self.__v += self.g
            self.position = (x, y)
            if y == self.to_pos[1]:
                self.__state = 3
        else:
            x = self.get_new_position(x, self.to_pos[0], self.speed)
            self.position = (x, y)


class Sprite(pygame.sprite.Sprite):
    frame_num_increment = 0.25

    def __init__(self, position: (int, int), config: str):
        pygame.sprite.Sprite.__init__(self)
        # action
        self.__action = Idle()
        self.__action.position = position
        self.__actions_que = Queue()
        # frame
        self.__frame_num = 0.0
        self.__frames = defaultdict(list)
        self.__load_config_file(config)
        self.__rect = self.image.get_rect()
        self.__rect.move_ip(position)

    def add_action(self, action: Action):
        self.__actions_que.put(action)

    @property
    def image(self):
        if len(self.__frames[self.__action.pose]) == 0:
            self.__load_frame(self.__action.pose)
        if int(self.__frame_num) >= len(self.__frames[self.__action.pose]):
            self.__frame_num = 0.0
        if isinstance(self, Hero):
            print(self.__action.pose, int(self.__frame_num), self.__frame_num)
        return self.__frames[self.__action.pose][int(self.__frame_num)]

    @property
    def rect(self):
        return self.__rect

    @property
    def position(self) -> (int, int):
        return (self.__rect.left, self.__rect.top)

    @position.setter
    def position(self, pos: (int, int)):
        self.__rect.left, self.__rect.top = pos

    def __load_config_file(self, config: str):
        data = load_json(config)
        self.__sprite_img = load_image(data['image'])
        self.__frames_desc = data['poses']

    def __load_frame(self, name: str):
        print('__load_frame:', name)
        for frame_desc in self.__frames_desc[name]:
            frame_size = (int(frame_desc['width']), int(frame_desc['height']))
            frame_pos = (int(frame_desc['x']), int(frame_desc['y']))
            frame_surface = pygame.Surface(frame_size, pygame.SRCALPHA, 32)
            frame_surface.blit(self.__sprite_img, (0, 0),
                               (frame_pos, frame_size))
            self.__frames[name].append(frame_surface)

    def update(self):
        if self.__action.arrived() and not self.__actions_que.empty():
            # take a action from the queue
            self.__action = self.__actions_que.get()
            self.__action.position = self.position
            self.__frame_num = 0.0
        else:
            # update position of the action
            self.__frame_num += self.frame_num_increment
            self.__action.update()
        self.position = self.__action.position


class Hero(Sprite):
    pass


class Dragon(Sprite):
    pass


class Princess(Sprite):
    pass
