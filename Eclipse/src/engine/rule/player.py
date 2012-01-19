__author__="jglouis"
__date__ ="$Dec 22, 2011 5:56:50 PM$"

class Player(object):
    def __init__(self, faction):
        self.color = faction.color
        self.faction = faction
        self.victory_points = 0
        self.may_do = []
        self.to_do = []
    
    def add(self, action_klass, mandatory = False):
        """Add an action to either to_do or may_do list."""
        
    def is_allowed(self, action_klass):
        """Return True if the action is either in to_do or may_do list."""
        return action_klass in self.may_do + self.to_do
    
    def take(self, action_klass):
        """Remove a corresponding action either from to_do or may_do list."""
        try:
            self.to_do.remove(action_klass)
        except:
            self.may_do.remove(action_klass)