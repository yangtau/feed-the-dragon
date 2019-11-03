import pygame
import os
import json
from functools import lru_cache


__res_dir = os.path.dirname(__file__)

FONTS_DIR = os.path.join(__res_dir, 'fonts/')
THEME_DIR = os.path.join(__res_dir, 'theme/')


@lru_cache(maxsize=64)
def load_font(font_file_name: str, size):
    return pygame.font.Font(os.path.join(FONTS_DIR, font_file_name), size)


fonts = {
    "noto-sans": "NotoSansCJK-Regular.ttc",
    "noto-sans-bold": "NotoSansCJK-Bold.ttc"
}


@lru_cache(maxsize=64)
def get_font(font_name: str, size: int) -> pygame.font.Font:
    if font_name not in fonts:
        print('Warnning: {} is not found'.format(font_name))
        return pygame.font.SysFont(pygame.font.get_default_font(), size)
    return load_font(fonts[font_name], size)


@lru_cache(maxsize=64)
def load_image(filename: str):
    filepath = os.path.join(__res_dir, filename)
    return pygame.image.load(filepath).convert_alpha()


@lru_cache(maxsize=64)
def load_json(filename: str):
    filepath = os.path.join(__res_dir, filename)
    with open(filepath) as f:
        data = json.load(f)
    return data

def save_json(filename: str, json_obj):
    filepath = os.path.join(__res_dir, filename)
    with open(filepath, 'w') as f:
        json.dump(json_obj, f)
