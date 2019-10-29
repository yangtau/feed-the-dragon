import pygame
from collections import defaultdict
import surfaces
from resources.resource import load_json
from resources.resource import load_image


class Button(object):
    def __init__(self, m: surfaces.Map):
        self.__state1 = load_image('button/pause.png')
        self.__state0 = load_image('button/start.png')
        self.rect = self.__state1.get_rect()
        self.__m = m
        self.__state = 0

    @property
    def image(self):
        if self.__state == 0:
            return self.__state0
        else:
            return self.__state1

    def click(self):
        if self.__state == 0:
            self.__m.start()
        else:
            self.__m.reset()
        self.__state = 1-self.__state


class Game(object):
    '''A capsulation of pygame
    Attributes:
        ...
    '''

    def __init__(self, title: str, size: (int, int), fps=60):
        self.title = title
        self.size = size
        self.fps = fps
        self.surface = None
        self.clock = None
        self.tool_in_mouse = None
        self.force_refresh = False
        self.__event_handlers = defaultdict(list)
        self.__event_handlers[pygame.MOUSEBUTTONDOWN].append(self.drag_handler)
        self.__init_pygame()

    def set_map(self, m: surfaces.Map):
        self.__map = m

    def set_toolbox(self, toolbox: surfaces.Toolbox):
        self.__toolbox = toolbox

    def set_button(self, btn):
        self.__btn = btn

    def enroll_event_handler(self,
                             event: int,
                             handler: callable):
        '''enroll event handler
        Args:
            event: pygame.event.EventType.type, event type identifier
            handler: a function taking an event as argurment
        '''
        self.__event_handlers[event].append(handler)

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

    def run(self):
        '''start the game'''
        # draw background
        self.surface.fill((255, 255, 255))
        while True:
            self.clock.tick(self.fps)
            self.__event_handle()
            # TODO: remove the next line
            self.surface.fill((255, 255, 255))
            # if self.tool_in_mouse or self.force_refresh:
            #     self.surface.fill((255, 255, 255))
            self.__map.draw(self.surface)
            self.__toolbox.draw(self.surface)
            self.surface.blit(self.__btn.image, self.__btn.rect)
            # draw mouse
            if self.tool_in_mouse:
                self.tool_in_mouse.rect.center = pygame.mouse.get_pos()
                self.surface.blit(self.tool_in_mouse.texture,
                                  self.tool_in_mouse.rect)
            pygame.display.flip()
            self.force_refresh = False

    def __init_pygame(self):
        pygame.init()
        pygame.display.set_caption(self.title)
        self.surface = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()

    def __event_handle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            for handler in self.__event_handlers[event.type]:
                handler(event)


if __name__ == '__main__':
    size = (808, 700)
    game = Game('Feed the Dragon', size, 30)
    m = surfaces.Map('config/map-2.json', (20, 20))
    game.set_map(m)
    toolbox = surfaces.Toolbox('config/toolbox-1.json', (20, 616))
    game.set_toolbox(toolbox)
    btn = Button(m)
    btn.rect.center = (756, 648)
    game.set_button(btn)

    def btn_click(event):
        if event.button == 1 and btn.rect.collidepoint(pygame.mouse.get_pos()):
            btn.click()
    game.enroll_event_handler(pygame.MOUSEBUTTONDOWN, btn_click)
    game.run()
