import pygame
import os
from functools import lru_cache


@lru_cache(maxsize=64)
def load_image(filename):
    res_dir = './resources'
    filepath = os.path.join(res_dir, filename)
    return pygame.image.load(filepath).convert_alpha()
