'''
Created on 31 déc. 2011

@author: jglouis
'''

class Action(object):
    """
    Action represents the action that a player can take,
    mainly during the action phase.
    """
    def __init__(self, **kwargs):
        for key, value in kwargs:
            self.arg[key] = value
            
    def do(self):
        """
        do is the method to call to perform the action.
        """
        pass

class Reaction(Action):
    pass

class ReactionUpgrade(Reaction):
    def do(self):
        pass
    
class ReactionBuild(Reaction):
    def do(self):
        pass
    
class ReactionMove(Reaction):
    def do(self):
        pass

class Explore(Action):
    """
    take a tuple as an argument representing the coordinates for
    the sector to explore.
    """            
    def do(self):
        #check if the sector is allowed for exploration
        pass
    
class Influence(Action):
    def do(self):
        pass
        
class Research(Action):
    def do(self):
        pass
    
class Upgrade(Action):
    def do(self):
        pass
    
class Build(Action):
    def do(self):
        pass

class Move(Action):
    def do(self):
        pass