'''
@author: 冯准生
@email:1565853379@qq.com
@brief: 
    this file is a page which maneges the map_editor
'''
import pygame
import pygame_gui
from page_manager import PageBase, PageManager
import map_editor
from resources.resource import load_image, get_font, save_json, SETTINGS
import common


class EditorPage(PageBase):
    map_config_file = 'config/map_base.json'
    toolbox_config_file = 'config/elem_base.json'
    size = common.WIN_SIZE
    btn_size = (100,60)

    def __init__(self, pm):
        super().__init__(pm)
        #config
        self.__map = map_editor.MapBase(self.map_config_file, (20, 20))
        self.__elembox = map_editor.ElemBase(
            self.toolbox_config_file, (20, 616))
        self.__background = load_image(SETTINGS['background'])
        
        self.tool_in_mouse = None
        self.register_event_handler(pygame.MOUSEBUTTONDOWN, self.drag_handler)
        self.__init_btn()

    def __init_btn(self):
        btn_rect = pygame.Rect((self.size[0]-(20+self.btn_size[0]),
                                self.size[1]-20-self.btn_size[1]), self.btn_size)
        self.__input_box = pygame_gui.elements.UIButton(
                btn_rect, "完成", self.gui_manager)
        self.register_gui_event_handler(
            'ui_button_pressed',
            self.__input_box,
            lambda e: self.complete())
        
        exit_btn_rect = pygame.Rect((self.size[0]-2*(20+self.btn_size[0]),
                                     self.size[1]-20-self.btn_size[1]), self.btn_size)
        self.__exit_box = pygame_gui.elements.UIButton(
                exit_btn_rect, "退出", self.gui_manager)
        self.register_gui_event_handler(
                'ui_button_pressed',
                self.__exit_box,
                lambda e: self.page_manager.pop())

    def complete(self):
        self.elem_map = self.__map.get_elem_map()
        self.characters_pos = self.__map.get_character_pos()
        if self.characters_pos[0] == [] or self.characters_pos[1] == [] or self.characters_pos[2] == []:
            print("error: the value of three characters_pos has one which is None at least")
        else:
            self.page_manager.push(
                 MapNamePage(self.page_manager, self.elem_map,self.characters_pos))

    def drag_handler(self, event):
        assert event.type == pygame.MOUSEBUTTONDOWN
        # click left
        if event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.__map.rect.collidepoint(mouse_pos):
                if self.tool_in_mouse:
                    # put down a tool
                    self.__map.put_tool(mouse_pos, self.tool_in_mouse)
                    self.tool_in_mouse = None
                else:
                    # remove tool
                    self.__map.remove_tool(mouse_pos)
            if self.__elembox.rect.collidepoint(mouse_pos):
                if not self.tool_in_mouse:
                    self.tool_in_mouse = self.__elembox.get_elem(mouse_pos)
                    self.tool_in_mouse.rect = self.tool_in_mouse.texture.get_rect()
        # click right
        if event.button == 3:
            # throw away tool in hand
            if self.tool_in_mouse:
                self.tool_in_mouse = None
                self.force_refresh = True

    def draw(self, window_surface):
        window_surface.blit(self.__background, (0, 0))
        self.__map.draw(window_surface)
        self.__elembox.draw(window_surface)
        # draw mouse
        if self.tool_in_mouse:
            self.tool_in_mouse.rect.center = pygame.mouse.get_pos()
            window_surface.blit(self.tool_in_mouse.texture,
                                self.tool_in_mouse.rect)


class MapNamePage(PageBase):
    size = (808, 700)
    y_off = 30
    y_dis = 100
    
    # title
    title_str = '地图设置'
    title_text_size = 50
    title_color = (120, 120, 255)
    
    #tip
    tip_str = '(请按ENTER键保存)'
    tip_text_size = 30
    tip_color = (80, 80,80)
    
    #map_name
    map_name_str = '地图名称'
    map_name_text_size = 20
    map_name_color = (20,30,60)
    
    #toolbox
    toolbox_str = '工具数目（格式：u,d,l,r）'
    toolbox_text_size = 20
    toolbox_color = (50,180,120)


    def __init__(self, pm, elem, characters):
        super().__init__(pm)
        self.__background = load_image(SETTINGS['background'])
        self.elem_map = elem
        self.hero_pos = characters[0]
        self.dragon_pos = characters[1]
        self.princess_pos = characters[2]
        self.map_name = None
        self.toolbox_num = None
        self.__init_text()
        self.__init_input_box()
        self.__init_btn()

    def __init_text(self):
        #title
        font_title = get_font('noto-sans-bold', self.title_text_size)
        text_title = font_title.render(
            self.title_str, True, self.title_color)
        self.__title_text = text_title
        self.__title_pos = ((self.size[0]-text_title.get_width())//2,
                            self.y_off)
        
        #tip
        font_tip = get_font('noto-sans-bold', self.tip_text_size)
        text_tip = font_tip.render(self.tip_str, True, self.tip_color)
        self.tip_text = text_tip
        self.tip_pos = ((self.size[0]-text_tip.get_width())//2,self.y_off+self.y_dis)
            
        #map_name
        font_map_name = get_font('noto-sans-bold', self.map_name_text_size)
        text_map_name = font_map_name.render(
                self.map_name_str, True, self.map_name_color)
        self.__map_name_text = text_map_name
        self.__map_name_pos = ((self.size[0]-text_map_name.get_width())//2,
                               self.y_off+2*self.y_dis)
        #toolbox
        font_toolbox = get_font('noto-sans-bold', self.toolbox_text_size)
        text_toolbox = font_toolbox.render(
                self.toolbox_str, True, self.toolbox_color)
        self.__toolbox_text = text_toolbox
        self.__toolbox_pos = ((self.size[0]-text_toolbox.get_width())//2,
                              self.y_off+3*self.y_dis)

    def __init_input_box(self):
        #map_name
        map_name_rect = pygame.Rect((self.__map_name_pos[0]-80, 
                                     self.__map_name_pos[1]+2*self.map_name_text_size), 
                                    (240, 60))
        self.__map_box = pygame_gui.elements.UITextEntryLine(
            map_name_rect, self.gui_manager)
        self.register_gui_event_handler(
            'ui_text_entry_finished', self.__map_box,
            self.map_handler)
        
        #toolbox
        toolbox_rect = pygame.Rect((self.__toolbox_pos[0],
                                    self.__toolbox_pos[1]+2*self.toolbox_text_size),
                                    (240,60))
        self.__tool_box = pygame_gui.elements.UITextEntryLine(
                toolbox_rect, self.gui_manager)
        self.register_gui_event_handler(
                'ui_text_entry_finished', self.__tool_box,
                self.tool_handler)
        
    def __init_btn(self):
        btn_rect = pygame.Rect((600, 520), (100, 60))
        self.__input_box = pygame_gui.elements.UIButton(
            btn_rect, "完成", self.gui_manager)

        self.register_gui_event_handler(
            'ui_button_pressed',
            self.__input_box,
            lambda e: self.complete())
        
        exit_btn_rect = pygame.Rect((720,520),(100,60))
        self.__exit_box = pygame_gui.elements.UIButton(
                exit_btn_rect, "退出", self.gui_manager)
        self.register_gui_event_handler(
                'ui_button_pressed',
                self.__exit_box,
                lambda e: self.page_manager.pop())

    def map_handler(self, event):
        print("Entered text:", event.text)
        self.map_name = event.text
        
    def tool_handler(self, event):
        print("Entered text:", event.text)
        num_str = event.text.split(',')
        self.toolbox_num = list(map(int, num_str))
        
    def complete(self):
        if self.map_name == None or self.toolbox_num == None:
            print("error: map_name or toolbox_num is None!")
        else:    
            self.save_map(self.elem_map, self.hero_pos, self.dragon_pos,
                          self.princess_pos, self.map_name, self.toolbox_num)
            self.page_manager.pop(2)
        

    def draw(self, window_surface):
        window_surface.blit(self.__background, (0, 0))
        window_surface.blit(self.__title_text, self.__title_pos)
        window_surface.blit(self.tip_text, self.tip_pos)
        window_surface.blit(self.__map_name_text, self.__map_name_pos)
        window_surface.blit(self.__toolbox_text, self.__toolbox_pos)

    def save_map(self, elem_map, hero_pos, dragon_pos, princess_pos, map_name, toolbox_num):
        map_now = {}
        map_now['size'] = [14, 9]
        map_now['tile_size'] = [64, 64]
        map_now['background'] = "background/colored_talltrees.png"
        map_now['map'] = elem_map
        map_now['tiles'] = {
            "^": {
                "name": "grass",
                "texture": "tiles/grassMid.png"
            },
            "b": {
                    "name": "box",
                    "texture": "tiles/box.png"
            },
            ".": {
                "name": "blank"
            },
            "$": {
                "name": "rock",
                "texture": "tiles/grassCenter.png"
            },
            "w": {
                "name": "wall",
                "texture": "tiles/castleCenter.png"
            }
        }
        map_now['sprites'] = [
            {
                "name": "hero",
                "position": hero_pos,
                "json": "sprites/hero/character.json"
            },
            {
                "name": "dragon",
                "position": dragon_pos,
                "json": "sprites/zombie/character.json"
            },
            {
                "name": "princess",
                "position": princess_pos,
                "json": "sprites/princess/character.json"
            }
        ]
        map_now['toolbox'] = [
            {
              "name" : "up",
              "object_id" : "up_toolbox",
              "texture" : "tools/up.png",
              "number" : toolbox_num[0],
              "position" : []
            },
            {
              "name" : "down",
              "object_id" : "down_toolbox",
              "texture" : "tools/down.png",
              "number" : toolbox_num[1],
              "position" : []        
            },
            {
              "name" : "left",
              "object_id" : "left_toolbox",
              "texture" : "tools/left.png",
              "number" : toolbox_num[2],
              "position" : []
            },
            {
              "name" : "right",
              "object_id" : "right_toolbox",
              "texture" : "tools/right.png",
              "number" : toolbox_num[3],
              "position" : []
            },     
        ]           

        filename = 'config/%s.json' % map_name
        save_json(filename, map_now)


if __name__ == '__main__':
    pm1 = PageManager(common.WIN_SIZE, 'hello')
    pm1.push(EditorPage(pm1))
    pm1.run()
