'''
@author: yangtau
@mail: yanggtau+fd@gmail.com
@brief:
    the page where players play the game
'''
import pygame
import pygame_gui
from collections import defaultdict
from surface import MapSurface, Tool
from page_manager import PageBase, PageManager
from resources.resource import load_json, load_image


class Switch(object):
    def __init__(self, pos: (int, int)):
        self.__image1 = load_image('button/pause.png')
        self.__image0 = load_image('button/start.png')
        self.__state = 0
        self.__rect = self.__image0.get_rect()
        self.__rect.center = pos

    @property
    def rect(self):
        return self.__rect

    @property
    def surface(self):
        if self.__state == 0:
            return self.__image0
        else:
            return self.__image1

    def click(self):
        self.__state = 1-self.__state


class GamePage(PageBase):
    # map
    map_pos = (20, 10)
    tile_size = (64, 64)
    # toolbox
    tool_pos = (20, 606)
    tool_margin = 10
    tool_size = (64, 64)
    # switch
    switch_center_pos = (756, 648)

    def __init__(self, pm, map_config_file: str):
        super().__init__(pm)
        map_config = load_json(map_config_file)
        # map
        self.__map_surf = MapSurface(map_config)
        self.__map_surf_rect = self.__map_surf.surface.get_rect()
        self.__map_surf_rect.move_ip(self.map_pos)
        # background
        self.__background = load_image(map_config['background'])
        # toolbox
        self.__init_toolbox(map_config['toolbox'])
        # start_rest switch
        self.__switch = Switch(self.switch_center_pos)
        self.__start = False
        self.register_event_handler(
            pygame.MOUSEBUTTONDOWN, self.__switch_click_handler)
        # tool on mouse
        self.__tool_on_mouse = None
        self.__tool_on_mouse_rect = None
        # drag handler
        self.register_event_handler(
            pygame.MOUSEBUTTONDOWN, self.__tool_drag_handler)
        # tools on map
        self.__tools_on_map = []

    def __init_toolbox(self, toolbox_config):
        '''
        toolbox_config:
        [{"name":"", "object_id":"", "numbet":1}...]
        - object_id is used in pygame_gui.elements.UIButton, and it is defined 
        in resources/themes/theme.json.
        '''
        self.__tools = dict()
        tool_poss = [(i*(self.tool_size[0]+self.tool_margin)+self.tool_pos[0],
                      self.tool_pos[1]) for i in range(len(toolbox_config))]
        for pos, conf in zip(tool_poss, toolbox_config):
            tool_btn = pygame_gui.elements.UIButton(
                pygame.Rect(pos, self.tool_size), '', self.gui_manager,
                object_id=conf['object_id']
            )
            self.__tools[conf['name']] = Tool(conf, tool_btn)
            self.register_gui_event_handler(
                'ui_button_pressed', tool_btn,
                self.__get_tool_click_handler(conf['name']))

    def __get_tool_click_handler(self, name) -> callable:
        '''Return a gui event handler'''
        def handler(event):
            if self.__tool_on_mouse:
                return  # do nothing if there is already a tool on mouse
            tool = self.__tools[name]
            self.__tool_on_mouse = tool
            self.__tool_on_mouse_rect = tool.texture.get_rect()
            tool.dec_num()
        return handler

    def __tool_drag_handler(self, event):
        # click lift
        if event.button == 1:
            mous_x, mous_y = pygame.mouse.get_pos()
            if self.__map_surf_rect.collidepoint(mous_x, mous_y):
                map_x, map_y = self.map_pos
                rela_pos = (mous_x-map_x, mous_y-map_y)
                if self.__tool_on_mouse is not None:
                    # put down a tool
                    if self.__map_surf.put_tool(self.__tool_on_mouse, rela_pos):
                        # self.__tool_on_mouse.dec_num()
                        self.__tool_on_mouse = None
                else:
                    # remove tool
                    tool = self.__map_surf.remove_tool(rela_pos)
                    if tool is not None:
                        tool.inc_num()
        # click right
        if event.button == 3 and self.__tool_on_mouse is not None:
            # throw the tool on mouse
            self.__tool_on_mouse.inc_num()
            self.__tool_on_mouse = None

    def __switch_click_handler(self, event):
        btn = self.__switch
        if event.button == 1 and btn.rect.collidepoint(pygame.mouse.get_pos()):
            btn.click()
            if not self.__start:
                self.__start = True
                # self.__map.start()
            else:
                self.__start = False
                # self.__map.reset()

    def draw(self, win_surf):
        win_surf.blit(self.__background, (0, 0))
        win_surf.blit(self.__map_surf.surface, self.__map_surf_rect)
        win_surf.blit(self.__switch.surface, self.__switch.rect)

    def draw_after_gui(self, win_surf):
        # the tool on mouse should be drew on the top of toolbox
        if self.__tool_on_mouse:
            self.__tool_on_mouse_rect.center = pygame.mouse.get_pos()
            win_surf.blit(self.__tool_on_mouse.texture,
                          self.__tool_on_mouse_rect)


if __name__ == '__main__':
    pm = PageManager((808, 700), 'hello')
    pm.push(GamePage(pm, 'config/map-1.json'))
    pm.run()
