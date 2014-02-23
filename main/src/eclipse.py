from cocos.director import director

from gui.menu import MainMenuScene


__author__="jglouis"
__date__ ="$Dec 21, 2011 10:34:16 AM$"

if __name__ == "__main__":

    director.init(resizable = True)
        
    MainMenuScene()
