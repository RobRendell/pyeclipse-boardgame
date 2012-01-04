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
from cocos.tiles import HexMapLayer, HexCell

class BoardLayer(Layer):
    def __init__(self):
        super(BoardLayer, self).__init__()
        self.add(Label('BoardLayer'))
        
class PlayerBoardLayer(HexMapLayer):
    def __init__(self):
        super(PlayerBoardLayer, self).__init__(1,1,[HexCell(0,0,2)])
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
        self.add(ColorLayer(0,0,0,255), 0)
        self.add(BoardLayer(), 1)
        self.add(control_layer, 2)
        
class PlayerBoardScene(Scene):
    def __init__(self, control_layer):
        super(PlayerBoardScene, self).__init__()
        self.add(ColorLayer(200,200,200,255), 0)
        self.add(PlayerBoardLayer(), 1)
        self.add(control_layer, 2)
        

director.init()
control_layer = ControlLayer()
board_scene = BoardScene(control_layer)
player_board_scene = PlayerBoardScene(control_layer)
control_layer.control_list = [board_scene, player_board_scene]
director.run(board_scene)        