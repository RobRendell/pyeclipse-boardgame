'''
Created on 4 janv. 2012

@author: jglouis
'''

from cocos.director import director
from cocos.layer.base_layers import MultiplexLayer, Layer
from cocos.menu import MenuItem, ToggleMenuItem, Menu
from cocos.scene import Scene
from cocos.text import Label
import pyglet

from engine.rule.game import Game
from gui.play import MainScreen
from cocos.sprite import Sprite


#from cocos.particle import ParticleSystem, Color
#from cocos.euclid import Point2

pyglet.resource.path.append('../image')
pyglet.resource.reindex()

class MainMenuScene(Scene):
    def __init__(self):
        super(MainMenuScene, self).__init__()
        background = Sprite('eclipse.jpg')
        background.position = (director.get_window_size()[0]/2, director.get_window_size()[1]/2)
        self.add(background)
        multiplexLayer = MultiplexLayer(
                             MainMenu(),
                             OptionsMenu(),
                             AboutLayer())
        multiplexLayer.position = (0, -100)
        self.add(multiplexLayer, 1)
        director.run(self)

class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__()

        items = []
        
        items.append(MenuItem('New Game', self.on_new_game))
        items.append(MenuItem('Options', self.on_options))
        items.append(MenuItem('About', self.on_about))
        self.create_menu(items)

    def on_new_game(self):
        print 'launch game'
        game = Game(6)
        MainScreen(game)
        
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
        
