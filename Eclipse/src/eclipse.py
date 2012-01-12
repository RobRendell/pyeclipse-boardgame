import sys
sys.path.append('C:\\Users\\jglouis\\workspace\\Eclipse\\src\\material\\data')
print sys.path


from engine.rule.game import Game
from gui.play import MainScreen
import pyglet




__author__="jglouis"
__date__ ="$Dec 21, 2011 10:34:16 AM$"

if __name__ == "__main__":

    game = Game(6)
    pyglet.resource.path.append('gui')
    pyglet.resource.reindex()
    MainScreen(game)