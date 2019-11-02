import pygame
import pygame_gui
from collections import defaultdict
from resources.resource import THEME_DIR


class PageBase(object):
    def __init__(self, pm, size=None):
        self.__page_manager = pm
        if not size:
            size = pm.size
        self.__event_handlers = defaultdict(list)
        self.__gui_event_handlers = dict()
        self.__gui_manager = pygame_gui.UIManager(size, THEME_DIR+'theme.json')

    @property
    def page_manager(self):
        return self.__page_manager

    @property
    def gui_manager(self):
        return self.__gui_manager

    def draw(self, window_surface: pygame.Surface):
        '''Subclass should override this method'''
        pass

    def update(self, window_surface, time_delta):
        self.__gui_manager.update(time_delta)
        self.draw(window_surface)
        self.__gui_manager.draw_ui(window_surface)

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
        self.__gui_manager.process_events(event)
        for handler in self.__event_handlers[event.type]:
            handler(event)
        if event.type == pygame.USEREVENT:
            handler = self.__gui_event_handlers.get(
                (event.user_type, event.ui_element), None)
            if handler:
                handler(event)


class PageManager(object):
    def __init__(self, size: (int, int), title: str, fps=30):
        pygame.init()
        pygame.display.set_caption(title)
        self.__window = pygame.display.set_mode(size)
        self.__clock = pygame.time.Clock()
        self.__fps = fps
        self.__size = size
        self.__page_stack = []
        # init gui

    @property
    def size(self):
        return self.__size

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
            time_delta = self.__clock.tick(self.__fps) / 1000.0
            top_page = self.__page_stack[-1]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                top_page.event_handle(event)
            top_page.update(self.__window, time_delta)
            pygame.display.flip()
