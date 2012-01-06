'''
Created on 4 janv. 2012

@author: jglouis
'''
from cocos.scene import Scene
from cocos.layer.base_layers import Layer
from cocos.text import Label
from cocos.director import director
from cocos.scenes.transitions import FadeTRTransition, FadeBLTransition,\
    SlideInBTransition, SlideInTTransition
from cocos.layer.util_layers import ColorLayer
from cocos.tiles import HexMapLayer, HexCell, Tile, Resource
from cocos import tiles
from cocos.draw import Line
import math
from cocos.layer.scrolling import ScrollableLayer, ScrollingManager
import pyglet
from cocos.sprite import Sprite

class BoardLayer(ScrollableLayer):
    is_event_handler = True
    def __init__(self):
        self.px_width = 5000
        self.px_height = 5000
        super(BoardLayer, self).__init__()
        self.add(Label('BoardLayer'))
        ws = director.get_window_size()
        self.add(Sprite('milkyway.jpg', scale = 0.1, position = (500,500)))
        
    def on_mouse_press (self, x, y, buttons, modifiers):        
        x, y = self.scroller.pixel_from_screen(x,y)
        #self.scroller.set_focus(x,y)
        
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.scroller.scale += scroll_y * 0.1
        self.scroller.scale = min(max(self.scroller.scale, 0.2), 2)
                
    def on_key_press(self, key, modifiers):
        print key,modifiers
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers ):
        fx, fy = self.scroller.fx, self.scroller.fy
        
        #transformation needed for autoscale
        dx, dy = director.get_virtual_coordinates(x + dx, y + dy)
        x, y = director.get_virtual_coordinates(x, y)
        dx = dx - x
        dy = dy - y

        self.scroller.set_focus(fx-dx, fy-dy)
        
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
            director.replace(SlideInTTransition(self.control_list[1], duration = 0.2))
        elif key == 98:
            director.replace(SlideInBTransition(self.control_list[0], duration = 0.2))
        
class BoardScene(Scene):
    def __init__(self, control_layer):
        super(BoardScene, self).__init__()
        self.add(ColorLayer(10,10,10,255), 0)
        scroller = ScrollingManager()
        scroller.set_focus(500, 500)
        scroller.add(BoardLayer())
        self.add(scroller)
        self.add(control_layer, 2)
        
class PlayerBoardScene(Scene):
    def __init__(self, control_layer):
        super(PlayerBoardScene, self).__init__()
        self.add(ColorLayer(200,200,200,255), 0)
        self.add(PlayerBoardLayer(), 1)
        self.add(control_layer, 2)        

director.init(resizable = True, do_not_scale = False)
control_layer = ControlLayer()
board_scene = BoardScene(control_layer)
player_board_scene = PlayerBoardScene(control_layer)
control_layer.control_list = [board_scene, player_board_scene]
director.run(board_scene)