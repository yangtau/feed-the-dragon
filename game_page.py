'''
@author: yangtau
@mail: yanggtau+fd@gmail.com
@brief:
    the page where players play the game
'''
import pygame
import pygame_gui
from collections import defaultdict
import surface
from page_manager import PageBase, PageManager
from resources.resource import load_json
from resources.resource import load_image


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


class Tool(object):
    '''Tool
    Attr:
        texture
        name
    '''

    def __init__(self, tool_config: dict, btn: pygame_gui.elements.UIButton):
        self.__texture = load_image(tool_config['texture'])
        self.__name = tool_config['name']
        self.__count = tool_config['number']
        self.__btn = btn

    @property
    def button(self):
        return self.__btn

    @property
    def texture(self):
        return self.__texture

    @property
    def number(self):
        return self.__count

    @property
    def name(self) -> str:
        return self.__name

    def inc_num(self):
        self.__count += 1

    def dec_num(self):
        self.__count -= 1


class GamePage(PageBase):
    # map
    map_pos = (20, 10)
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
        self.__map_surf = surface.MapSurface(map_config)
        # background
        self.__background = load_image(map_config['background'])
        # draw map on background, reduce one blit call
        self.__background.blit(self.__map_surf.surface, self.map_pos)
        # toolbox
        self.__init_toolbox(map_config['toolbox'])
        # start_rest switch
        self.__switch = Switch(self.switch_center_pos)
        self.__start = False

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
            print(name)
        return handler

    def __tool_drag_handler(self, event):
        pass

    def __btn_click(self, event):
        btn = self.__switch
        if event.button == 1 and btn.rect.collidepoint(pygame.mouse.get_pos()):
            btn.click()
            if not self.__start:
                self.__start = True
                # self.__map.start()
            else:
                self.__start = False
                # self.__map.reset()

    def __update_tools(self):
        for tool in self.__tools.values():
            tool.button.set_text(str(tool.number))
            if tool.number == 0:
                tool.button.disable()
                tool.button.redraw()
            else:
                # TODO: enable it only if needed
                tool.button.enable()
                tool.button.redraw()

    def draw(self, win_surf):
        self.__update_tools()
        win_surf.blit(self.__background, (0, 0))
        win_surf.blit(self.__switch.surface, self.__switch.rect)

        '''
        # button
        self.__start = False
        self.__btn = Switch()
        self.__btn.rect.center = (756, 648)
        self.tool_in_mouse = None
        self.force_refresh = False
        # register event handlers
        self.register_event_handler(pygame.MOUSEBUTTONDOWN, self.btn_click)
        self.register_event_handler(pygame.MOUSEBUTTONDOWN, self.drag_handler)


    def drag_handler(self, event):
        # click left
        if event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.__map.rect.collidepoint(mouse_pos):
                if self.tool_in_mouse:
                    # put down a tool
                    # TODO: what if there is already a tool in the mouse_pos
                    self.__map.put_tool(mouse_pos, self.tool_in_mouse)
                    self.tool_in_mouse = None
                else:
                    # remove tool
                    self.__map.remove_tool(mouse_pos)
            if self.__toolbox.rect.collidepoint(mouse_pos):
                if not self.tool_in_mouse:
                    self.tool_in_mouse = self.__toolbox.get_tool(mouse_pos)
                    self.tool_in_mouse.rect = self.tool_in_mouse.texture.get_rect()
        # click right
        if event.button == 3:
            # throw away tool in hand
            if self.tool_in_mouse:
                self.tool_in_mouse = None
                self.force_refresh = True
    def draw(self, window_surface):
        window_surface.blit(self.__background, (0, -200))
        window_surface.blit(self.__btn.image, self.__btn.rect)
        # draw mouse
        if self.tool_in_mouse:
            self.tool_in_mouse.rect.center = pygame.mouse.get_pos()
            window_surface.blit(self.tool_in_mouse.texture,
                                self.tool_in_mouse.rect)
        self.force_refresh = False

'''


if __name__ == '__main__':
    pm = PageManager((808, 700), 'hello')
    pm.push(GamePage(pm, 'config/map-1.json'))
    pm.run()
