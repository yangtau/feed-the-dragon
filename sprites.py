import pygame
from queue import Queue
from collections import defaultdict
from resources.resource import load_image
from resources.resource import load_json


class Action(object):
    # poses
    walk = 'walk'
    run = 'run'
    idle = 'idle'

    def __init__(self, pose: str,  to_pos: (int, int)):
        self.__pose = pose
        self.__to_pos = to_pos
        self.__position = None

    @property
    def pose(self):
        return self.__pose

    @property
    def to_pos(self):
        return self.__to_pos

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, pos: (int, int)):
        self.__position = pos

    def arrived(self):
        return self.position == self.to_pos

    def update(self, speed: int):
        '''update the position'''
        def fn(_from: int, _to: int):
            if _to < _from:
                return _from - min(speed, _from - _to)
            else:
                return _from + min(speed, _to - _from)
        self.position = (fn(self.position[0], self.to_pos[0]),
                         fn(self.position[1], self.to_pos[1]))
    def __str__(self):
        return '"%s" %s' % (self.pose, self.to_pos)


class Sprite(pygame.sprite.Sprite):
    default_pose = Action.idle
    frame_num_increment = 0.25
    speed = 3

    def __init__(self, position: (int, int), config: str):
        pygame.sprite.Sprite.__init__(self)
        # action
        self.__action = Action(self.default_pose, position)
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
        print(action)

    @property
    def image(self):
        if len(self.__frames[self.__action.pose]) == 0:
            self.__load_frame(self.__action.pose)
        if int(self.__frame_num) >= len(self.__frames):
            self.__frame_num = 0.0
        return self.__frames[self.__action.pose][int(self.__frame_num)]

    @property
    def rect(self):
        return self.__rect

    @property
    def position(self):
        return (self.__rect.left, self.__rect.top)

    @position.setter
    def position(self, pos: (int, int)):
        self.__rect.left, self.__rect.top = pos

    def __load_config_file(self, config: str):
        data = load_json(config)
        self.__sprite_img = load_image(data['image'])
        self.__frames_desc = data['poses']

    def __load_frame(self, name: str):
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
            self.__action.update(self.speed)
        self.position = self.__action.position


class Hero(Sprite):
    def __init__(self, position: (int, int), config: str):
        super().__init__(position, config)


class Dragon(Sprite):
    def __init__(self, position: (int, int), config: str):
        super().__init__(position, config)


class Princess(Sprite):
    def __init__(self, position: (int, int), config: str):
        super().__init__(position, config)
