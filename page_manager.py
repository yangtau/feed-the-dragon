import pygame
import pygame_gui
from collections import defaultdict


class PageBase(object):
    def __init__(self, pm: PageManager):
        self.pageManager = pm
        self.__event_handlers = defaultdict(list)
        self.__gui_event_handlers = dict()

    @property
    def surface(self):
        pass

    def register_event_handler(self, event_id: int, handler: callable):
        '''Register a normal event handler.
           Note: the handler shall take an event as the argument.
        '''
        self.__event_handlers[event_id].append(handler)

    def remove_event_handler(self, event_id: int, handler: callable):
        self.__event_handlers[event_id].remove(handler)

    def register_gui_event_handler(self, user_type: str,
                                   ui_element, handler: callable):
        '''Register handlers for UI elements.
           Note: there can be only one handler for a specific 
                 (user_type, ui_element).
        '''
        self.__gui_event_handlers[(user_type, ui_element)] = handler

    def remove_gui_event_handler(self, user_type: str, ui_element):
        self.__gui_event_handlers.pop((user_type, ui_element))

    def event_handle(self, event):
        for handler in self.__event_handlers[event.type]:
            handler(event)
        if event.type == pygame.USEREVENT:
            handler = self.__gui_event_handlers[(event.user_type, event.ui_element)]
            handler(event)


class PageManager(object):
    def __init__(self, init_page: PageBase, size: (int, int), title: str, fps=30):
        pygame.init()
        pygame.display.set_caption(title)
        self.__window = pygame.display.set_mode(size)
        self.__clock = pygame.time.Clock()
        self.__fps = fps
        self.__page_stack = [init_page]

    def push(self, page: PageBase):
        self.__page_stack.append(page)

    def pop(self):
        self.__page_stack.pop()
        if len(self.__page_stack) == 0:
            # Exit when there is no page in the stack
            pygame.quit()
            exit()

    def run(self):
        while True:
            self.__clock.tick(self.__fps)
            top_page = self.__page_stack[-1]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                top_page.event_handle(event)
            self.__window.blit(top_page.surface, (0, 0))
            self.__window.flip()
