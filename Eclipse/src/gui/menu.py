'''
Created on 4 janv. 2012

@author: jglouis
'''

from cocos.text import Label
from cocos.director import director
from cocos.menu import MenuItem, ToggleMenuItem, Menu
from cocos.scene import Scene
from cocos.layer.base_layers import MultiplexLayer, Layer

class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__('ECLIPSE')
        
        items = []
        
        items.append(MenuItem('New Game', self.on_new_game))
        items.append(MenuItem('Options', self.on_options))
        items.append(MenuItem('About', self.on_about))
        self.create_menu(items)
        
    def on_new_game(self):
        print 'launch game'
        
    def on_options(self):
        self.parent.switch_to(1)
    
    def on_about(self):
        self.parent.switch_to(2)
    
class OptionsMenu(Menu):
    def __init__(self):
        super(OptionsMenu, self).__init__('Options')
        items = []
        
        items.append(ToggleMenuItem('Full screen: ', self.on_full_screen))
        items.append(MenuItem('Back', self.on_quit))
        self.create_menu(items)
        
    def on_full_screen(self, value):
        director.window.set_fullscreen(value) #@UndefinedVariable
        
    def on_quit(self):
        self.parent.switch_to(0)
        
class AboutLayer(Layer):
    def __init__(self):
        super(AboutLayer, self).__init__()
        cprght = Label('Game Developed by Jean-Guillaume Louis - 2012')
        self.add(cprght)
        
    def on_quit(self):
        self.parent.switch_to(0)
    
director.init(resizable = True)
scene = Scene()
scene.add(MultiplexLayer(
                         MainMenu(),
                         OptionsMenu(),
                         AboutLayer()))
director.run(scene)
        
