import pygame
import pygame.locals
import random

black = (0, 0, 0)
white = (255, 255, 255)
window_size = (1200, 900)
block_size = (64, 64)

'''
+----------> X
|
|
|
|
|
V Y
'''

pygame.init()
window = pygame.display.set_mode(window_size)
wall_img = pygame.image.load('wall-2-64.png').convert()
pacman_img = pygame.image.load('pacman-64.png').convert()
cxk_img = pygame.image.load('cxk-64.png').convert()
ball_img = pygame.image.load('ball-64.png').convert()

tile_table = [[wall_img if random.randint(
    0, 10) > 7 else None for _ in range(12)] for _ in range(12)]
left_margin = (window_size[0] - len(tile_table[0]) * block_size[0]) // 2
table_rct = ((left_margin, 0),
             (left_margin+block_size[0]*len(tile_table[0]),
              block_size[1] * len(tile_table)))
obj_in_mouse = None

toolbar = [pacman_img]

toolbar_left_margin = left_margin + 20
toolbar_top_margin = block_size[1] * len(tile_table) + 10
toolbar_rct = ((toolbar_left_margin, toolbar_top_margin),
               (toolbar_left_margin+block_size[0]*len(toolbar),
                toolbar_top_margin+block_size[1]))

tools_in_table = []


def get_obj_in_position(pos):
    x, y = pos
    if x >= table_rct[0][0] and x <= table_rct[1][0] and \
       y >= table_rct[0][1] and y <= table_rct[1][1]:
        return 'table'
    elif x >= toolbar_rct[0][0] and x <= toolbar_rct[1][0] and \
            y >= toolbar_rct[0][1] and y <= toolbar_rct[1][1]:
        return 'tool'
    else:
        return None


def get_tool_obj(pos):
    x = pos[0]-toolbar_left_margin
    return (toolbar[x//block_size[0]], pos)


def render():
    window.fill(white)
    # draw tile
    for x, row in enumerate(tile_table):
        for y, tile in enumerate(row):
            if tile:
                window.blit(
                    tile, (x*(block_size[0])+left_margin, y*(block_size[1])))
    for x, tool in enumerate(toolbar):
        window.blit(
            tool, (x*block_size[0]+toolbar_left_margin,
                   toolbar_top_margin))
    for tool in tools_in_table:
        window.blit(*tool)

    if obj_in_mouse:
        window.blit(*obj_in_mouse)

    pygame.display.flip()


def click(event):
    pos = pygame.mouse.get_pos()
    global moving
    global obj_in_mouse
    obj_in_pos = get_obj_in_position(pos)
    if obj_in_mouse:
        obj_in_mouse = (obj_in_mouse[0],
                        (pos[0] - block_size[0]//2,
                         pos[1]-block_size[1]//2))

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if obj_in_mouse:
            # put
            print(pos)
            if obj_in_pos == 'table':
                x, y = pos
                x_indx = (x-left_margin)//block_size[0]
                y_indx = y//block_size[1]
                obj_in_mouse = (obj_in_mouse[0],
                                (x_indx * block_size[0] + left_margin,
                                 y_indx * block_size[1]))
                tools_in_table.append(obj_in_mouse)
            obj_in_mouse = None

        else:
            if obj_in_pos == 'tool':
                obj_in_mouse = get_tool_obj(pos)


def run():
    render()
    while True:
        for event in pygame.event.get():
            if event == pygame.QUIT:
                exit(0)
            click(event)
        render()


if __name__ == '__main__':
    run()
