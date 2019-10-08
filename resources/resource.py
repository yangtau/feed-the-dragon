import pygame
import os


def load_image(filename):
    res_dir = './resources'
    filepath = os.path.join(res_dir, filename)
    return pygame.image.load(filepath).convert_alpha()
