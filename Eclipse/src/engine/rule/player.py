__author__="jglouis"
__date__ ="$Dec 22, 2011 5:56:50 PM$"

class Player(object):
    def __init__(self, faction):
        self.color = faction.color
        self.faction = faction
        self.victory_points = 0