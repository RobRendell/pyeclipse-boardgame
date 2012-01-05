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

class BoardLayer(HexMapLayer):
    is_event_handler = True
    def __init__(self):
        #tile = Tile(2, None, 'C:\Users\jglouis\Pictures\space.jpg', None)
        super(BoardLayer, self).__init__(1,100,[[HexCell(0, 0, 1000, None, None)]])
        self.add(Label('BoardLayer'))
        self.set_cell_color(0, 0, (50,50,50))
        self.set_cell_opacity(0, 0, 255)
        self.set_dirty()
        
    def draw(self):    
        self.add_hex((50,50), 40)
        self.add_hex((50 + 60 ,50 + 20 * math.sqrt(3)), 40)
        self.add_hex((50,50 + 40 * math.sqrt(3)), 40)
        self.add_hex((50 - 60 ,50 + 20 * math.sqrt(3)), 40)
        
    def add_hex(self, centre, r):        
        hex_coord = []
        hex_centre = centre
        hex_r = r
        hex_coord.append((hex_centre[0] + hex_r/2,      hex_centre[1] + math.sqrt(3)*hex_r/2))
        hex_coord.append((hex_centre[0] + hex_r,        hex_centre[1] + 0))
        hex_coord.append((hex_centre[0] + hex_r/2,      hex_centre[1] - math.sqrt(3)*hex_r/2))
        hex_coord.append((hex_centre[0] - hex_r/2,      hex_centre[1] - math.sqrt(3)*hex_r/2))
        hex_coord.append((hex_centre[0] - hex_r,        hex_centre[1] + 0))
        hex_coord.append((hex_centre[0] - hex_r/2,      hex_centre[1] + math.sqrt(3)*hex_r/2))
        
        w = 3
        
        line1 = Line(hex_coord[0], hex_coord[1],(255,255,255,255) , w)
        line2 = Line(hex_coord[1], hex_coord[2],(255,255,255,255) , w)
        line3 = Line(hex_coord[2], hex_coord[3],(255,255,255,255) , w)
        line4 = Line(hex_coord[3], hex_coord[4],(255,255,255,255) , w)
        line5 = Line(hex_coord[4], hex_coord[5],(255,255,255,255) , w)
        line6 = Line(hex_coord[5], hex_coord[0],(255,255,255,255) , w)
        self.add(line1)
        self.add(line2)
        self.add(line3)
        self.add(line4)
        self.add(line5)
        self.add(line6)
        
        print self.get_visible_cells()
        
    def on_mouse_press (self, x, y, buttons, modifiers):
        x, y = director.get_virtual_coordinates (x, y)
        print x,y, self.get_at_pixel(int(x), int(y))
        
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
        #self.add(ColorLayer(0,0,0,255), 0)
        self.add(BoardLayer(), 1)
        hex_layer = tiles.load('hexmap.xml')['map0']
        self.add(control_layer, 2)
        
class PlayerBoardScene(Scene):
    def __init__(self, control_layer):
        super(PlayerBoardScene, self).__init__()
        self.add(ColorLayer(200,200,200,255), 0)
        self.add(PlayerBoardLayer(), 1)
        self.add(control_layer, 2)        

director.init(resizable = True, width = 800, height = 800)
control_layer = ControlLayer()
board_scene = BoardScene(control_layer)
player_board_scene = PlayerBoardScene(control_layer)
control_layer.control_list = [board_scene, player_board_scene]
director.run(board_scene)        