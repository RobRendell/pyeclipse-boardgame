__author__="jglouis"
__date__ ="$Dec 21, 2011 10:35:50 AM$"
import zone as zn

class Component(object):
    """
    Components are the real game objects manipulated by the players.
    Each component must belong to one game zone at any time.
    """
    def when_placed(self, game):
        pass

class PersonalComponent(Component):
    """A PersonnalComponent is a component with one owner."""
    def __init__(self, owner):
        self.owner = owner
        
class PlayerBoard(PersonalComponent):
    def __init__(self, owner, ship_parts_supply):
        super(PlayerBoard, self).__init__(owner)
        self.blueprints = zn.BlueprintBoard(owner, ship_parts_supply)
        self.resource_track = zn.ResourceTrack(owner)
        self.population_track = zn.PopulationTrack(owner)
        self.population_cemetery = zn.PopulationCemetery(owner)
        self.influence_track = zn.InfluenceTrack(owner)
        self.technology_track = zn.TechnologyTrack(owner)
        self.faction = owner.faction

class SectorTile(Component):
    """An hexagon tile."""
    def __init__(self, id, name, victory_points, n_money = 0, nr_money = 0,
    n_science = 0, nr_science = 0, n_material = 0, nr_material = 0, n_wild = 0,
    discovery = False, n_ancients = 0, artifact = False, wormholes = 1):
        self.id = id
        self.name = name
        self.victory_points = victory_points
        self.n_money = n_money
        self.nr_money = nr_money
        self.n_science = n_science
        self.nr_science = nr_science
        self.n_material = n_material
        self.nr_material = nr_material
        self.n_wild = n_wild        
        self.discovery = discovery
        self.n_ancients = n_ancients
        self.artifact = artifact
        self.wormholes = wormholes
        self.components = []

    def add(self, component):
        """Add a component to the tile."""
        self.components.append(component)

    def remove(self, component):
        """Remove a component from the tile."""
        self.components.remove(component)

    def when_placed(self, game):
        #place the components indicated on the tile
        if self.discovery:
            self.add(game.discovery_tiles_draw_pile.draw())
        if self.n_ancients == -1:
            self.add(GalacticCenterDefenseSystem())
        else:
            for dummy in range(self.n_ancients):
                self.add(AncientShip())
        #create the resource slots
        self.science_slot = [None for dummy in range(self.n_science)]
        self.r_science_slot = [None for dummy in range(self.nr_science)]
        self.money_slot = [None for dummy in range(self.n_money)]
        self.r_money_slot = [None for dummy in range(self.nr_money)]
        self.material_slot = [None for dummy in range(self.n_material)]
        self.r_material_slot = [None for dummy in range(self.nr_material)]

class TechnologyTile(Component):
    """A research tile."""
    def __init__(self, name, cost = None, min_cost = None, category = None, type = None):
        """
        type is either ship_part, build, instant or None
        category is either military, grid or nano
        """
        self.name = name
        self.cost = cost
        self.min_cost = min_cost
        self.type = type
        self.category = category

class ShipPartTile(Component):
    def __init__(self, name, technology_required = False, initiative = 0,
    movement = 0, computer = 0, shield =0, hull = 0, missile = False,
    energy_produced = 0, energy_consumed = 0, hits = 1, n_dice = 0,
    discovery = False):
        self.name = name
        self.technology_required = technology_required
        self.initiative = initiative
        self.movement = movement
        self.computer = computer
        self.shield = shield
        self.hull = hull
        self.missile = missile
        self.energy_produced = energy_produced
        self.energy_consumed = energy_consumed
        self.hits = hits
        self.n_dice = n_dice
        self.discovery = discovery

class DiscoveryTile(Component):
    def __init__(self, type, money = 0, science = 0, material = 0,
    ship_part_name = None, initiative = 0, movement = 0, computer = 0,
    shield = 0, hull = 0, missile = False, energy_produced = 0,
    energy_consumed = 0, hits = 0, n_dice = 0):

        self.type = type
        if type == 'resource':
            self.money = money
            self.science = science
            self.material = material
        elif type == 'tech' or type == 'cruiser':
            pass
        elif type == 'ship_part':
            self.ship_part_tile = ShipPartTile(
                ship_part_name,
                False,
                initiative,
                movement,
                computer,
                shield,
                hull,
                missile,
                energy_produced,
                energy_consumed,
                hits,
                n_dice,
                True
            )

class AmbassadorTile(PersonalComponent):
    def __init__(self, owner):
        super(AmbassadorTile, self).__init__(owner)
        self.victory_points = 1

    def give_to(self, receiver):
        self.receiver = receiver

class Monolith(Component):
    def __init__(self):
        self.victory_points = 3

class Orbital(Component):
    pass

class ColonyShip(PersonalComponent):
    def __init__(self, owner):
        super(ColonyShip, self).__init__(owner)
        self.activated = False

    def refresh(self):
        self.activated = False

    def use(self):
        if self.activated:
            return False
        else:
            self.activated = True
            return True

class AncientShip(Component):
    def __init__(self):
        self.initiative = 2
        self.computer = 1
        self.shield = 0
        self.hull = 1
        self.cannons = [1,1]
        self.missiles = []

class GalacticCenterDefenseSystem(Component):
    def __init__(self):
        self.initiative = 0
        self.computer = 1
        self.shield = 0
        self.hull = 7
        self.cannons = [1,1,1,1]
        self.missiles = []

class ReputationTile(Component):
    def __init__(self, victory_points):
        self.victory_points = victory_points

class TraitorCard(Component):
    def __init__(self):
        self.victory_points = -2
        self.owner = None

    def give_to(self, owner):
        self.owner = owner

class Ship(PersonalComponent):
    def __init__(self, owner, type):
        """Type may be interceptor, cruiser, dreadnought or starbase"""
        super(Ship, self).__init__(owner)
        self.type = type
        self.color = owner.color

class InfluenceDisc(PersonalComponent):
    def __init__(self, owner):
        super(InfluenceDisc, self).__init__(owner)
        self.color = owner.color

class PopulationCube(PersonalComponent):
    def __init__(self, owner):
        super(PopulationCube, self).__init__(owner)
        self.color = owner.color