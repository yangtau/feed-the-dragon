import pygame
from collections import defaultdict
import surfaces


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
        self.components = []
        self.__event_handlers = defaultdict(list)
        self.__event_handlers[pygame.MOUSEBUTTONDOWN].append(self.drag_handler)
        self.__init_pygame()

    def add_component(self, component: surfaces.Surface):
        '''every component must have surface and rect'''
        self.components.append(component)

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
        assert event.type == pygame.MOUSEBUTTONDOWN
        # click left
        if event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for cpt in self.components:
                if cpt.rect.collidepoint(mouse_pos):
                    # there is a tool in hand, put it down
                    '''
                    TODO:
                    put down: 1. there is a tool already
                              2. there can be placed a tool
                    remove the tool in a pos
                    '''
                    if self.tool_in_mouse and isinstance(cpt, surfaces.Map):
                        cpt.put_obj_in(mouse_pos, self.tool_in_mouse)
                        self.tool_in_mouse = None
                    # no tool in hand, pick up one
                    if not self.tool_in_mouse and \
                            isinstance(cpt, surfaces.Toolbox):
                        self.tool_in_mouse = cpt.get_obj_in(mouse_pos)
                        self.tool_in_mouse['rect'] = \
                            self.tool_in_mouse['texture'].get_rect()
                        print(self.tool_in_mouse)
                    break
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
            # FIXME: delete this if there is no blank in surface
            if self.tool_in_mouse or self.force_refresh:
                self.surface.fill((255, 255, 255))
            for cmpt in self.components:
                # if there is a tool in mouse, then surface must be updated
                if cmpt.is_updated or self.tool_in_mouse or self.force_refresh:
                    print(cmpt, 'updated')
                    self.surface.blit(cmpt.surface, cmpt.rect)
                    cmpt.is_updated = False
            # draw mouse
            if self.tool_in_mouse:
                self.tool_in_mouse['rect'].center = pygame.mouse.get_pos()
                self.surface.blit(self.tool_in_mouse['texture'],
                                  self.tool_in_mouse['rect'])
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
    size = (900, 800)
    game = Game('Feed the Dragon', size, 30)
    m = surfaces.Map('./level-1.map', (30, 10))
    toolbox = surfaces.Toolbox('./level-1.toolbox', (30, 650))
    game.add_component(m)
    game.add_component(toolbox)
    game.run()
