'''
Created on 4 janv. 2012

@author: jglouis
'''
from cocos.scene import Scene
from cocos.layer.base_layers import Layer
from cocos.text import Label
from cocos.director import director
from cocos.scenes.transitions import FadeTRTransition, FadeBLTransition,\
    SlideInBTransition, SlideInTTransition, FadeUpTransition, FadeDownTransition
from cocos.layer.util_layers import ColorLayer
from cocos.tiles import HexMapLayer, HexCell, Tile, Resource
from cocos import tiles
from cocos.draw import Line
import math
from cocos.layer.scrolling import ScrollableLayer, ScrollingManager
import pyglet
from cocos.sprite import Sprite
from hexmanager import HexManager

class BoardLayer(ScrollableLayer):
    is_event_handler = True
    def __init__(self, scroller):
        self.px_width = 5000
        self.px_height = 5000
        super(BoardLayer, self).__init__()
        self.add(Label('BoardLayer'))
        self.add(Sprite('milkyway.jpg', scale = 0.5, position = (self.px_width / 2, self.px_height / 2)))
        self.add(Sprite(pyglet.resource.animation('planet.gif'), scale = 0.5, position = (self.px_width / 2, self.px_height / 2)))
        self.hex_width = 200
        self.hex_manager = HexManager(self.hex_width, (self.px_width / 2, self.px_height / 2))
        self.scroller = scroller
        self.scroller.set_focus(self.px_width / 2, self.px_height / 2)
        
    def on_mouse_press (self, x, y, buttons, modifiers):        
        x, y = self.scroller.pixel_from_screen(x,y)
        hex_u, hex_v = self.hex_manager.get_hex_from_rect_coord(x, y)
        print 'hex', (hex_u, hex_v)
        print 'rect', self.scroller.pixel_from_screen(x,y)
        
    def on_mouse_motion(self, x, y, dx, dy):    
        x, y = self.scroller.pixel_from_screen(x,y)
        hex_u, hex_v = self.hex_manager.get_hex_from_rect_coord(x, y)
        hex_x, hex_y = self.hex_manager.get_rect_coord_from_hex_coord(hex_u, hex_v)
        for child in self.get_children():
            if isinstance(child, Line):
                child.kill()
        self.add_hex((hex_x, hex_y), self.hex_width / 2)
        
        
    def add_hex(self, centre, r):        
        hex_coord = []
        hex_centre = centre
        hex_r = r
        hex_coord.append((hex_centre[0],                hex_centre[1] + 2 * hex_r / math.sqrt(3)))
        hex_coord.append((hex_centre[0] + hex_r,        hex_centre[1] + hex_r / math.sqrt(3)))
        hex_coord.append((hex_centre[0] + hex_r,        hex_centre[1] - hex_r / math.sqrt(3)))
        hex_coord.append((hex_centre[0],                hex_centre[1] - 2 * hex_r / math.sqrt(3)))
        hex_coord.append((hex_centre[0] - hex_r,        hex_centre[1] - hex_r / math.sqrt(3)))
        hex_coord.append((hex_centre[0] - hex_r,        hex_centre[1] + hex_r / math.sqrt(3)))       
        w = 3        
        line1 = Line(hex_coord[0], hex_coord[1],(255,255,255,255) , w)
        line2 = Line(hex_coord[1], hex_coord[2],(255,255,255,255) , w)
        line3 = Line(hex_coord[2], hex_coord[3],(255,255,255,255) , w)
        line4 = Line(hex_coord[3], hex_coord[4],(255,255,255,255) , w)
        line5 = Line(hex_coord[4], hex_coord[5],(255,255,255,255) , w)
        line6 = Line(hex_coord[5], hex_coord[0],(255,255,255,255) , w)
        self.add(line1, 2)
        self.add(line2, 2)
        self.add(line3, 2)
        self.add(line4, 2)
        self.add(line5, 2)
        self.add(line6, 2)   
        
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.scroller.scale += scroll_y * 0.1
        self.scroller.scale = min(max(self.scroller.scale, 0.2), 2)
                
    def on_key_press(self, key, modifiers):
        print key,modifiers
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers ):
        fx, fy = self.scroller.fx, self.scroller.fy
        xdx, ydy = self.scroller.pixel_from_screen(x + dx, y + dy)
        x, y = self.scroller.pixel_from_screen(x, y)        
        dx = xdx - x
        dy = ydy - y
        #ws_x, ws_y = director.get_window_size()
        x_focus = fx - dx
        y_focus = fy - dy
        self.scroller.set_focus(x_focus, y_focus)
        
    def on_enter(self):
        super(BoardLayer, self).on_enter()
        self.scroller = self.get_ancestor(ScrollingManager)
        
class PlayerBoardLayer(Layer):
    def __init__(self):
        super(PlayerBoardLayer, self).__init__()
        self.add(Label('PlayerBoardLayer'))
        
        
class ReasearchTrackLayer(Layer):
    def __init__(self):
        super(ReasearchTrackLayer, self).__init__()
        
class ActionLayer(Layer):
    def __init__(self):
        super(ActionLayer, self).__init__()
        
class ControlLayer(Layer):
    is_event_handler = True    
    def __init__(self):
        super(ControlLayer, self).__init__()
        
    def on_key_press(self, key, modifiers):
        if key == 112:
            director.replace(FadeDownTransition(self.control_list[1], duration = 0.2))
        elif key == 98:
            director.replace(FadeUpTransition(self.control_list[0], duration = 0.2))
        
class BoardScene(Scene):
    def __init__(self, control_layer):
        super(BoardScene, self).__init__()
        self.add(ColorLayer(0,0,0,255), 0)
        scroller = ScrollingManager()
        scroller.add(BoardLayer(scroller))
        self.add(scroller)
        self.add(control_layer, 2)
        
class PlayerBoardScene(Scene):
    def __init__(self, control_layer):
        super(PlayerBoardScene, self).__init__()
        self.add(ColorLayer(200,200,200,255), 0)
        self.add(PlayerBoardLayer(), 1)
        self.add(control_layer, 2)
        
class MainScreen(object):
    def __init__(self, Game):  
        director.init(fullscreen = False, resizable = True, do_not_scale = False)
        self.control_layer = ControlLayer()
        board_scene = BoardScene(self.control_layer)
        player_board_scene = PlayerBoardScene(self.control_layer)
        self.control_layer.control_list = [board_scene, player_board_scene]
        director.run(board_scene)
        
if __name__ == "__main__":
    MainScreen(None)