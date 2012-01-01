import random
import component as cp

__author__="jglouis"
__date__ ="$Dec 21, 2011 10:49:19 AM$"

class Zone(object):
    def __init__(self, owner = None):
        self.owner = owner

    def get_content(self):
        """Return either a list/dict of components or the number of components."""
        return None

class Board(Zone):
    def __init__(self, game):
        super(Board, self).__init__()
        self.hex_grid = {} #a dictionary coord->tile
        self.game = game

    def add(self, coord, component):
        """Add the specified component to the given coordinates on the board."""
        self.hex_grid[coord] = component
        component.when_placed(self.game)

    def get_content(self):
        return self.hex_grid

class DrawPile(Zone):
    def __init__(self, list):
        super(DrawPile, self).__init__()
        self.content = list
        self.discard_pile = DiscardPile()
        self.shuffle()
        
    def draw(self):
        """
        Return the first item from the pile, removing the item from the pile.
        Return None if the drawpile was empty.
        """
        try :
            item = self.content.pop(0)
        except:
            print 'unable to draw'
            return None
        #rehuffle the discard pile to create a new drawpile if the last item was drawn
        if len(self.content) == 0 and len(self.discard_pile.content) != 0:
            self.content.extend(self.discard_pile.content)
            self.discard_pile.content = []
            self.shuffle()
        return item

    def shuffle(self):
        random.shuffle(self.content)

    def get_content(self):
        return len(self.content)

class DiscardPile(Zone):
    def __init__(self):
        super(DiscardPile, self).__init__()
        self.content = []

    def add(self, item):
        """Add an item in the discard pile."""
        self.content.append(item)

class Bag(Zone):
    def __init__(self, list):
        super(Bag, self).__init__()
        self.content = list
        self.shuffle()

    def draw(self):
        try:
            item = random.choice(self.content)
            self.remove(item)
            return item
        except:
            return None

    def shuffle(self):
        random.shuffle(self.content)

class BlueprintBoard(Zone):
    def __init__(self, owner,  ship_parts_supply):
        super(BlueprintBoard, self).__init__(owner)
        s = ship_parts_supply
        self.ship_blueprints_default = {
            'interceptor':[
                None,
                s.get('ion cannon'),
                s.get('nuclear source'),
                s.get('nuclear drive')
            ],
            'cruiser':[
                s.get('hull'),
                None,
                s.get('ion cannon'),
                s.get('nuclear source'),
                s.get('electron computer'),
                s.get('nuclear drive')
            ],
            'dreadnought':[
                s.get('ion cannon'),
                s.get('hull'),
                None,
                s.get('hull'),
                s.get('nuclear source'),
                s.get('ion cannon'),
                s.get('electron computer'),
                s.get('nuclear drive')
            ],
            'starbase':[
                s.get('hull'),
                s.get('ion cannon'),
                s.get('hull'),
                None,
                s.get('electron computer')
            ]
        }
        self.ship_blueprints = {
            'interceptor':[None for dummy in range(4)],
            'cruiser':[None for dummy in range(6)],
            'dreadnought':[None for dummy in range(8)],
            'starbase':[None for dummy in range(5)]
        }

    def get_stats(self, ship_class):
        pass

class ResourceTrack(Zone):
    def __init__(self, owner):
        super(ResourceTrack, self).__init__(owner)
        self.money = owner.faction.starting_money
        self.science = owner.faction.starting_science
        self.material = owner.faction.starting_material
        
class PopulationTrack(Zone):
    def __init__(self, owner):
        super(PopulationTrack, self).__init__(owner)
        self.population_track = {
            'money':[],
            'science':[],
            'material':[]
        }

    def take(self, track):
        """Take and remove a population cube from a track."""
        if len(self.population_track[track]) == 0:
            return None
        else:
            return self.population_track[track].pop()

    def add(self, track, population_cube):
        self.population_track[track].append(population_cube)

    def get_income(self):
        """
        Calculate the income from each population track and return it in a
        dict.
        """
        pass


class PopulationCemetery(Zone):
    def __init__(self, owner):
        super(PopulationCemetery, self).__init__(owner)
        self.population_cemetery = {
            'money':[],
            'science':[],
            'material':[]
        }

class InfluenceTrack(Zone):
    def __init__(self, owner):
        super(InfluenceTrack, self).__init__(owner)
        self.influence_track = []
        
    def add(self, influence_disc):
        self.influence_track.append(influence_disc)

    def get_upkeep(self):
        pass

class TechnologyTrack(Zone):
    def __init__(self, owner):
        super(TechnologyTrack, self).__init__(owner)
        self.technologies = {
            'military':[],
            'grid':[],
            'nano':[]
        }
        starting_technologies = owner.faction.starting_technologies
        for tech in starting_technologies:
            self.technologies[tech.category].append(tech)

class ReputationTrack(Zone):
    def __init__(self, owner):
        super(ReputationTrack, self).__init__(owner)
        self.track = {
            'diplomacy':[],
            'reputation':[]
        }
        self.reputation_max = owner.faction.reputation_only + owner.faction.reputation_diplomacy
        self.diplomacy_max = owner.faction.diplomacy_only + owner.faction.reputation_diplomacy

    def add(self, component):
        """
        Add a reputation tile or an ambassador to the track if there is space
        available.
        """
        if len(self.track['reputation']) + len(self.track['diplomacy']) <= 5:
            if isinstance(component, cp.ReputationTile):
                if len(self.track['reputation']) < self.reputation_max:
                    self.track['reputation'].append('reputation')
            elif isinstance(component, cp.AmbassadorTile):
                if len(self.track['diplomacy']) < self.diplomacy_max:
                    self.track['diplomacy'].append('reputation')

    def remove(self, component):
        """Remove a component from the reputation track."""
        if isinstance(component, cp.AmbassadorTile):
            self.track['diplomacy'].remove(component)
        else:
            self.track['reputation'].remove(component)

    def get_content(self):
        return self.track

class ResearchTrack(Zone):
    def __init__(self):
        super(ResearchTrack, self).__init__()
        self.technologies = []

    def add(self, technology_tile):
        """Add a new technology tile to the track"""
        self.technologies.append(technology_tile)

    def remove(self, technology_tile):
        """Remove the technology from the track"""
        self.technologies.remove(technology_tile)

    def get_content(self):
        return self.technologies

class ShipPartsTilesSupply(Zone):
    def __init__(self, ship_parts):
        super(ShipPartsTilesSupply, self).__init__(self)
        self.supply = dict([(sp.name, sp) for sp in ship_parts])

    def get(self, tech_name):
        """Return the technology tile with the specified given name"""
        return self.supply[tech_name]
    
class PersonalSupply(Zone):
    """
    The personal supply is meant to contain all the components owned by a player
    that are not yet on the board or on the player board. Components like
    ambassadors, ships and colony ships are by default in this zone at the start
    of the game.
    """
    def __init__(self, owner):
        super(PersonalSupply, self).__init__(owner)
        self.components = []
        
    def add(self, component):
        self.components.append(component)
        
    def remove(self, component):
        self.components.remove(component)
        
    def get_content(self):
        return self.components