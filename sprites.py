'''
@author: yangtau
@email: yanggtau+fd@gmail.com
@brief: 
    the sprite of roles in game
'''
import pygame
import math
from queue import Queue
from collections import defaultdict
from resources.resource import load_sprite_image, load_json, play_sound
import common


class Action(object):
    def __init__(self, to_pos: (int, int)):
        self.__to_pos = to_pos
        self.__position = None

    @property
    def pose(self) -> str:
        pass

    @property
    def reversed(self) -> bool:
        return self.to_pos[0] < self.position[0]

    @property
    def to_pos(self) -> (int, int):
        return self.__to_pos

    @property
    def position(self) -> (int, int):
        return self.__position

    @position.setter
    def position(self, pos: (int, int)):
        self.__position = pos

    @property
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

    @property
    def arrived(self):
        return True

    @property
    def to_pos(self):
        return self.position

    @property
    def reversed(self):
        return False

    @property
    def pose(self):
        return 'idle'

    def update(self):
        pass


class Cheer(Idle):
    number = 50
    @property
    def pose(self):
        return 'cheer'

    @property
    def arrived(self):
        return False

    def __init__(self, action_event=None):
        super().__init__()
        self.__acc = 0
        self.__event = action_event

    def update(self):
        self.__acc += 1
        if self.__acc == self.number and self.__event is not None:
            self.__event()


class Attack(Idle):
    @property
    def pose(self):
        return 'attack'


class Walk(Action):
    @property
    def speed(self):
        return 4

    @property
    def pose(self):
        return 'walk'

    def update(self):
        self.position = (self.get_new_position(self.position[0], self.to_pos[0], self.speed),
                         self.get_new_position(self.position[1], self.to_pos[1], self.speed))


class FallDown(Walk):
    def __init__(self, des_pos, action_done_event: callable = None):
        super().__init__(des_pos)
        self.__event = action_done_event

    @property
    def speed(self):
        return 10

    @property
    def pose(self):
        return 'fallDown'

    def update(self):
        super().update()
        if self.arrived and self.__event is not None:
            self.__event()


class Fly(Walk):
    def __init__(self, des_pos):
        super().__init__(des_pos)

    @property
    def speed(self):
        return 10

    @property
    def pose(self):
        if self.to_pos[1] < self.position[1]:
            return 'jump'
        elif self.to_pos[1] < self.position[1]:
            return 'fall'
        elif self.to_pos[0] != self.position[0]:
            return 'shove'
        else:
            return 'idle'

    def update(self):
        super().update()


class Fall(Action):
    '''
    Attr:
        state: 0 not active
               1 rise and linearly move
               2 fall and linearly move
               3 idle
    '''
    g = 0.4  # gravitational acceleration
    speed = 3  # speed of linearly moving

    def __init__(self, to_pos: (int, int)):
        super().__init__(to_pos)
        self.__state = 0

    @property
    def pose(self):
        if self.__state == 0:
            return 'walk'
        elif self.__state == 1:
            return 'jump'
        else:
            return 'fall'

    def update(self):
        x, y = self.position
        if self.__state == 0:
            if self.to_pos[0] - x >= 64 - 30:
                x = self.get_new_position(x, self.to_pos[0], self.speed)
            else:
                self.__state = 1
                # - 24 means that the top position of the action is
                # 24 pixel higher than the position.
                self.__top_point = y - 24
                # sum(V0, V1, ..., Vn) = h, V_n = V_{n-1} - a
                self.__v = math.sqrt(2 * self.g * (y - self.__top_point))
        elif self.__state == 1:
            y = int(self.get_new_position(y, self.__top_point, self.__v)+0.5)
            x = self.get_new_position(x, self.to_pos[0], self.speed)
            self.__v -= self.g
            # assert self.__v > 0
            if y == self.__top_point:
                self.__state = 2
                self.__v = 0
        elif self.__state == 2:
            y = int(self.get_new_position(y, self.to_pos[1], self.__v)+0.5)
            x = self.get_new_position(x, self.to_pos[0], self.speed)
            self.__v += self.g
            if self.position == self.to_pos:
                self.__state = 3
        self.position = (x, y)


class Jump(Action):
    '''
    Attr:
        state: 0 not active
               1 rise
               2 fall and linearly move
               3 linearly move
               4 idle
    '''
    g = 0.4  # gravitational acceleration
    speed = 3  # speed of linearly moving

    def __init__(self, to_pos: (int, int)):
        super().__init__(to_pos)
        self.__state = 0

    @property
    def pose(self):
        if self.__state == 1:
            return 'jump'
        elif self.__state == 2:
            return 'fall'
        else:
            return 'walk'

    def update(self):
        x, y = self.position
        if self.__state == 0:
            if self.to_pos[0] - x >= 64 - 30:
                x = self.get_new_position(x, self.to_pos[0], self.speed)
            else:
                self.__state = 1
                # - 24 means that the top position of the action is
                # 24 pixel higher than the to_pos.
                self.__top_point = self.to_pos[1] - 24
                # sum(V0, V1, ..., Vn) = h, V_n = V_{n-1} - a
                self.__v = math.sqrt(2 * self.g * (y - self.__top_point))
        elif self.__state == 1:
            y = int(self.get_new_position(y, self.__top_point, self.__v)+0.5)
            self.__v -= self.g
            # assert self.__v > 0
            if y == self.__top_point:
                self.__state = 2
                self.__v = 0
        elif self.__state == 2:
            y = int(self.get_new_position(y, self.to_pos[1], self.__v)+0.5)
            x = self.get_new_position(x, self.to_pos[0], self.speed)
            self.__v += self.g
            if y == self.to_pos[1]:
                self.__state = 3
        elif self.__state == 3:
            x = self.get_new_position(x, self.to_pos[0], self.speed)
            if self.position == self.to_pos:
                self.__state = 4
        self.position = (x, y)


class Sprite(pygame.sprite.Sprite):
    frame_num_increment = 0.2

    def __init__(self, position: (int, int), config: str, default_action: Action = Idle()):
        pygame.sprite.Sprite.__init__(self)
        # action
        self.__default_action = default_action
        self.__action = default_action
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

    def clear_actions(self):
        '''terminate the current action, and go to `pos`'''
        self.__action = self.__default_action
        while not self.__actions_que.empty():
            self.__actions_que.get()

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
        self.__sprite_img = load_sprite_image(data['image'])
        self.__frames_desc = data['poses']

    @property
    def image(self):
        pose = self.__action.pose
        if self.__action.reversed:
            # pose + '!': the name of the flip frame
            pose = pose+'!'
        if len(self.__frames[pose]) == 0:
            self.__load_frame(pose)
        if int(self.__frame_num) >= len(self.__frames[pose]):
            self.__frame_num = 0.0
        return self.__frames[pose][int(self.__frame_num)]

    def __load_frame(self, name: str):
        if name.endswith('!'):
            if len(self.__frames[name[:-1]]) == 0:
                self.__load_frame(name[:-1])
            for frame in self.__frames[name[:-1]]:
                flip = pygame.transform.flip(frame, True, False)
                self.__frames[name].append(flip)
        else:
            for frame_desc in self.__frames_desc[name]:
                frame_size = (int(frame_desc['width']), int(
                    frame_desc['height']))
                frame_pos = (int(frame_desc['x']), int(frame_desc['y']))
                frame_surface = pygame.Surface(frame_size, pygame.SRCALPHA, 32)
                frame_surface.blit(self.__sprite_img, (0, 0),
                                   (frame_pos, frame_size))
                self.__frames[name].append(frame_surface)

    def update(self):
        if self.__action.arrived:
            if not self.__actions_que.empty():
                # take a action from the queue
                self.__action = self.__actions_que.get()
                self.__action.position = self.position
                self.__frame_num = 0.0
            else:
                # default_action
                self.__action = self.__default_action
                self.__action.position = self.position
        self.__frame_num += self.frame_num_increment
        self.__action.update()
        self.position = self.__action.position


class Hero(Sprite):
    pass


class Dragon(Sprite):
    frame_num_increment = 0.1

    def __init__(self, position: (int, int), config: str):
        super().__init__(position, config, Attack())


class Princess(Sprite):
    frame_num_increment = 0.2

    def __init__(self, position: (int, int), config: str):
        super().__init__(position, config, Idle())
