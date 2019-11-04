import pygame
import os
import json
from functools import lru_cache


RES_DIR = os.path.dirname(__file__)

FONTS_DIR = os.path.join(RES_DIR, 'fonts/')
THEME_DIR = os.path.join(RES_DIR, 'theme/')


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
    filepath = os.path.join(RES_DIR, filename)
    return pygame.image.load(filepath).convert_alpha()


@lru_cache(maxsize=64)
def load_json(filename: str):
    filepath = os.path.join(RES_DIR, filename)
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f, encoding='utf-8')
    return data

def save_json(filename: str, json_obj):
    filepath = os.path.join(RES_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(json_obj, f, encoding='utf-8')
