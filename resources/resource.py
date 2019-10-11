import pygame
import os
import json
from functools import lru_cache


__res_dir = './resources'

@lru_cache(maxsize=64)
def load_image(filename: str):
    filepath = os.path.join(__res_dir, filename)
    return pygame.image.load(filepath).convert_alpha()


def load_json(filename: str):
    filepath =os.path.join(__res_dir, filename)
    with open(filepath) as f:
        data = json.load(f)
    return data
