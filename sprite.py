import pygame
from resources.resource import load_image

# TODO: sprite image


'''
{
    "walk": [
        {"x":, "y", "height":, "width"},
        {...},
        ...
    ],
    ...
}
'''
class Sprite(object):
    def __init__(self, filename: str, init_pos: (int, int)):
        self.img = self.load_file(filename)
        self.size = (70, 70)  # TODO: load it from file
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        self.rect = self.surface.get_rect()
        self.rect.move_ip(init_pos)
        self.to_x, self.to_y = init_pos
        self.speed = 2

    def move(self, x=None, y=None):
        '''straight line only, x or y must be set'''
        assert (x is not None or y is not None) and not (
            x is not None and y is not None)
        if x:
            self.to_x = x
        else:
            self.to_x = self.rect.left
        if y:
            self.to_y = y
        else:
            self.to_y = self.rect.top

    def draw(self, surface):
        if self.to_x != self.rect.left:
            self.rect.left += self.__get_speed(self.rect.left, self.to_x)
        if self.to_y != self.rect.top:
            self.rect.top += self.__get_speed(self.rect.top, self.to_y)
        self.surface.blit(self.img, (10, 0))
        surface.blit(self.surface, self.rect)

    def __get_speed(self, from_p, to_p):
        speed = self.speed
        if from_p > to_p:
            speed = -speed
        return min(speed, to_p - from_p)

    def load_file(self, filename: str):
        return load_image(filename)
