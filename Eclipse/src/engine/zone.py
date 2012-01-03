import random
import component as cp

__author__="jglouis"
__date__ ="$Dec 21, 2011 10:49:19 AM$"

class Zone(object):
    def __init__(self, owner = None, *args):
        self.owner = owner
        self.components = []
        for c in args:
            self.components.add(c)

    def get_content(self):
        """Return either a list/dict of components or the number of components."""
        return self.components
    
    def add(self, component):
        """Add a component to the zone."""
        self.components.append(component)
        
    def take(self, component = None):
        """return a component and remove it from the zone."""
        if component is None:
            return self.components.pop()        
        self.components.remove(component)
        return component

class Board(Zone):
    def __init__(self, game):
        #super(Board, self).__init__()
        self.hex_grid = {} #a dictionary coord->Sector
        self.game = game

    def add(self, coord, component):
        """Add the specified component to the given coordinates on the board."""
        if isinstance(component, cp.SectorTile):
            sector = Sector(component)
            self.hex_grid[coord] = sector
            #place discovery tiles
            if component.discovery:
                sector.add(self.game.discovery_tiles_draw_pile.draw())
            #place ancients ships/galactic center
            if component.n_ancients == -1:
                sector.add(cp.GalacticCenterDefenseSystem())
            else:
                for dummy in range(component.n_ancients):
                    sector.add(cp.AncientShip())
            #create resource slots
            for dummy in range(component.n_money):
                sector.add(ResourceSlot(resource_type = 'money'))
            for dummy in range(component.nr_money):
                sector.add(ResourceSlot(resource_type = 'money', advanced = 'True'))
            for dummy in range(component.n_science):
                sector.add(ResourceSlot(resource_type = 'science'))
            for dummy in range(component.nr_science):
                sector.add(ResourceSlot(resource_type = 'science', advanced = 'True'))
            for dummy in range(component.n_material):
                sector.add(ResourceSlot(resource_type = 'material'))
            for dummy in range(component.nr_material):
                sector.add(ResourceSlot(resource_type = 'material', advanced = 'True'))
            for dummy in range(component.n_wild):
                sector.add(ResourceSlot())
        else:
            self.hex_grid[coord].add(component)
        
    def take(self, component):        
        pass

    def get_content(self, coord = None):
        """
        If coord is not given, then it returns the whole board dictionary.
        If coord is given, then it returns the content of the corresponding hex.
        The first item of the list is always the sector itself.
        """
        if coord is None:
            return self.hex_grid
        return [self.hex_grid[coord]] + self.hex_grid[coord].get_content()
    
class ResourceSlot(Zone):
    """A slot for a population cube."""
    def __init__(self, owner = None, resource_type = None, advanced = False):
        """If resource type is not given or None, the slot will be wild."""
        super(ResourceSlot, self).__init__(owner)
        self.resource_type = resource_type
        self.advanced = advanced
        
    def isEmpty(self):
        """Return True if no population cubes, False otherwise."""
        return not len(self.components)
    
class Sector(Zone):
    """Represents a non-empty hex from the board"""
    def __init__(self, sector_tile):
        super(Sector, self).__init__(sector_tile)
        self.name = sector_tile.name
        self.id = sector_tile.id

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
    def take(self, component = None, component_type = None):
        if component is None:
            return self.components.pop()        
        if component_type is not None:
            component = [comp for comp in self.components if comp.type == component_type][0]
        self.components.remove(component)
        return component
