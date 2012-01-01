'''
Created on 31 déc. 2011

@author: jglouis
'''
import engine.zone as zn
import engine.component as cp

class Action(object):
    """
    Action represents the action that a player can take,
    mainly during the action phase.
    """
    def do(self, *args, **kwargs):
        """
        do is the method to call to perform the action during the game
        """
        pass

class Explore(Action):
    def do(self, coord):
        """
        take a tuple as an argument representing the coordinates for
        the sector to explore.
        """
        #check if the sector is allowed for exploration
        