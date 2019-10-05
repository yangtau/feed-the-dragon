import pygame
from collections import defaultdict
import surfaces


class Game(object):
    '''A capsulation of pygame
    Attributes:
        ...
    '''

    def __init__(self, title: str, width: int, height: int, fps=60):
        self.title = title
        self.width = width
        self.height = height
        self.fps = fps
        self.surface = None
        self.clock = None
        self.__map = None
        self.__toolbox = None
        self.__event_handlers = defaultdict(list)
        self.__init_pygame()

    def set_map(self, m: surfaces.Map):
        self.__map = m

    def set_toolbox(self, toolbox: surfaces.Toolbox):
        self.__toolbox = toolbox

    def __init_pygame(self):
        pygame.init()
        pygame.display.set_caption(self.title)
        self.surface = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

    def enroll_event_handler(self,
                             event: int,
                             handler: callable):
        '''enroll event handler
        Args:
            event: pygame.event.EventType.type, event type identifier
            handler: a function taking an event as argurment
        '''
        self.__event_handlers[event].append(handler)

    def __event_handle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            for handler in self.__event_handlers[event.type]:
                handler(event)

    def run(self):
        '''start the game'''
        # draw background
        self.surface.fill((255, 255, 255))
        while True:
            self.clock.tick(self.fps)
            self.__event_handle()
            # draw map
            left_margin = (self.width - self.__map.get_size()[0])//2
            if self.__map.get_is_updated():
                print('update map')
                self.surface.blit(self.__map.get_surface(), (left_margin, 0))
            # draw toolbox
            left_margin = (self.width - self.__toolbox.get_size()[0])//2
            top_margin = self.__map.get_size()[1] + 10
            if self.__toolbox.get_is_updated():
                print('update toolbox')
                self.surface.blit(self.__toolbox.get_surface(),
                                  (left_margin, top_margin))
            pygame.display.flip()


if __name__ == '__main__':
    game = Game('Feed the Dragon', 1000, 700, 30)
    m = surfaces.Map('./level-1.map')
    toolbox = surfaces.Toolbox('./level-1.toolbox')
    game.set_map(m)
    game.set_toolbox(toolbox)
    game.run()
