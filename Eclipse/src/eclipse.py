import sys
sys.path.append('C:\\Users\\jglouis\\workspace\\Eclipse\\src\\material\\data')
print sys.path


from engine.rule.game import Game
from gui.play import MainScreen

class Controller(object):
    """
    The controller acts as an intermediate between the gui and the engine.
    It translates mouse and keyboard events into behaviors. Each behavior 
    is linked with a game method. 
    """
    def __init__(self, game, gui):
        self.game = game
        self.gui = gui

class Behavior(object):
    """
    A Behavior is a sequence of mouse/keyboard events associated to
    a game modification.
    """
    pass

__author__="jglouis"
__date__ ="$Dec 21, 2011 10:34:16 AM$"

if __name__ == "__main__":

    game = Game(6)
    ms = MainScreen(game)
    
    