import pygame
from queue import Queue
from collections import defaultdict
from resources.resource import load_image
from resources.resource import load_json


class Sprite(pygame.sprite.Sprite):
    default_pos = 'idle'
    frame_num_cnt_increment = 0.2

    # TODO: normalize the size of sprites, and remove the size argu
    def __init__(self, size: (int, int), position: (int, int), config: str):
        # super.__init__(self)
        pygame.sprite.Sprite.__init__(self)
        self.__frames = defaultdict(list)
        self.__size = size
        self.__load_config_file(config)
        self.__current_frame_num = 0
        self.__pose = self.default_pos
        self.__current_frame = self.get_frame(self.__pose, 0)
        self.__rect = self.__current_frame.get_rect()
        self.__to_x, self.__to_y = position
        self.__rect.move_ip(position)
        self.__frame_num_cnt = 0.1
        self.__actions_que = Queue()

    def add_action(self, action):
        self.__actions_que.put(action)

    @property
    def pose(self):
        return self.__pose

    @pose.setter
    def pose(self, pose: str):
        if pose not in self.__frames_desc:
            raise Exception('No such pose: %s' % pose)
        self.__pose = pose

    @property
    def rect(self):
        return self.__rect

    @property
    def image(self):
        return self.__current_frame

    def __load_config_file(self, config: str):
        data = load_json(config)
        self.__sprite_img = load_image(data['image'])
        self.__frames_desc = data['poses']

    def __load_frame(self, name: str):
        for frame_desc in self.__frames_desc[name]:
            frame_size = (int(frame_desc['width']), int(frame_desc['height']))
            frame_pos = (int(frame_desc['x']), int(frame_desc['y']))
            # only support interger factor scale
            resize_factor = max(frame_size[0] // self.__size[0],
                                frame_size[1] // self.__size[1])
            new_size = (frame_size[0] // resize_factor,
                        frame_size[1] // resize_factor)

            frame_surface = pygame.Surface(frame_size, pygame.SRCALPHA, 32)
            frame_surface.blit(self.__sprite_img, (0, 0),
                               (frame_pos, frame_size))
            if resize_factor != 1:
                frame_surface = pygame.transform.smoothscale(
                    frame_surface, new_size)
            self.__frames[name].append(frame_surface)

    def get_frame(self, name: str, num: int):
        if len(self.__frames[name]) == 0:
            self.__load_frame(name)
        if len(self.__frames[name]) == 0:
            # fail to load frame
            raise Exception('No such frame: %s' % name)
        mod = num % len(self.__frames[name])
        return self.__frames[name][mod]

    def move(self, speed: int, x=None, y=None):
        if x:
            self.__to_x = x
        else:
            self.__to_x = self.__rect.left
        if y:
            self.__to_y = y
        else:
            self.__to_y = self.__rect.top
        self.__speed = speed

    def update(self):
        if self.__to_x != self.__rect.left:
            self.__rect.left += self.__get_speed(self.__rect.left, self.__to_x)
        if self.__to_y != self.__rect.top:
            self.__rect.top += self.__get_speed(self.__rect.top, self.__to_y)

        self.__frame_num_cnt += self.frame_num_cnt_increment
        self.__current_frame_num = int(self.__frame_num_cnt)
        self.__current_frame = self.get_frame(
            self.pose, self.__current_frame_num)

    def __get_speed(self, from_p, to_p):
        speed = self.__speed
        if from_p > to_p:
            speed = -speed
        return min(speed, to_p - from_p)


class Hero(Sprite):
    def __init__(self, size: (int, int), position: (int, int), config: str):
        super().__init__(size, position, config)


class Dragon(Sprite):
    def __init__(self, size: (int, int), position: (int, int), config: str):
        super().__init__(size, position, config)
