import random
import engine.zone as zn
import engine.component as cp
import engine.rule.player as pl
import material.discoverytiles as dt
import material.reputationtiles as rt
import material.sectortiles as st
import material.shipparts as sp
import material.technologytiles as tt
import material.factions as fa
from engine.zone import Sector

__author__="jglouis"
__date__ ="$Dec 22, 2011 5:56:29 PM$"

class Game(object):
    def __init__(self, n_players):
        #creating the players
        factions = fa.factions
        self.players = []
        for dummy in range(n_players):
            rand_faction = random.choice(factions)
            factions = [faction for faction in factions if faction.color != rand_faction.color]
            self.players.append(pl.Player(rand_faction))

        #create the bag of technology tiles
        self.technology_tiles_bag = zn.Bag(tt.technology_tiles)

        #create the bag of reputation tiles
        self.reputations_tiles_bag = zn.Bag(rt.reputation_tiles)

        #create the pile of discovery tiles
        self.discovery_tiles_draw_pile = zn.DrawPile(dt.discovery_tiles)

        #create a traitor card
        self.traitor_card = cp.TraitorCard()

        #create the board
        self.board = zn.Board(self)

        #add the galactic center
        self.board.add((0,0), st.galactic_center[0])

        #create the 3 drawpiles for the sectors
        self.inner_sectors_drawpile = zn.DrawPile(st.inner_hexes)
        self.middle_sectors_drawpile = zn.DrawPile(st.middle_hexes)
        self.outer_sectors_drawpile = zn.DrawPile(st.outer_hexes)
        
        #...then remove the adequate number of sector form the outer draw pile
        n = {2 : 13,
             3 : 8,
             4 : 4,
             5 : 2,
             6 : 0}[n_players]
        for dummy in range(n):
            self.outer_sectors_drawpile.draw()
        
        #choose a first player
        random.shuffle(self.players)
        #self.current_player = self.players[0]
        self.player_iterator = self.next_player()
        self.current_player = self.player_iterator.next()
        
        #assign a personal board, a starting hex and a personal supply to each player
        for n, player in enumerate(self.players):
            player.personal_board = zn.PlayerBoard(player)
            player.starting_hex = dict([(h.id, h) for h in st.starting_hexes])[player.faction.sector]
                              
            player.personal_supply = zn.PersonalSupply(player)
            for dummy in range(8):   
                player.personal_supply.add(cp.Interceptor(player))
            for dummy in range(4):
                player.personal_supply.add(cp.Cruiser(player))
            for dummy in range(2):
                player.personal_supply.add(cp.Dreadnought(player))
            for dummy in range(4):
                player.personal_supply.add(cp.Starbase(player))
            for dummy in range(3):
                player.personal_supply.add(cp.AmbassadorTile(player))
            for dummy in range(player.faction.colony_ships):
                player.personal_supply.add(cp.ColonyShip(player))
            for dummy in range(player.faction.starting_influence):
                player.personal_board.influence_track.add(cp.InfluenceDisc(player))
            for dummy in range(11):
                for resource_type in ['money', 'science', 'material']:
                    player.personal_board.population_track.add(cp.PopulationCube(player), resource_type)
                    
            #place the starting hexes on the board and populate them with one influence disc,
            #the starting ship, and as many population cubes as needed
            if n_players == 2:
                coord = [(2,2),(-2,-2)][n]
                rot = [0, 0][n] 
            elif n_players == 3:
                coord = [(2,2),(2,-2),(-4,0)][n]  
                rot = [0, 2, 1][n] 
            elif n_players == 4:
                coord =[(4,0),(2,-2),(-4,-0),(-2,2)][n]
                rot = [1, 1, 1, 1][n] 
            elif n_players == 5:
                coord = [(2,2),(4,0),(2,-2),(-2,-2),(-4,0)][n] 
                rot = [0, 1, 2, 2, 0][n] 
            elif n_players == 6:
                coord = [(2,2),(4,0),(2,-2),(-2,-2),(-4,0),(-2,2)][n] 
                rot = [0, 1, 2, 0, 1, 2][n]             
            self.board.add(coord, player.starting_hex, rot)
            self.board.add(coord, player.personal_board.influence_track.take())
            self.board.add(coord, player.personal_supply.take(
                                                              component_type = {'interceptor' : cp.Interceptor,
                                                                                'cruiser' : cp.Cruiser                                                                              
                                                                                }[player.faction.starting_unit]
                                                              ))
#             self.board.add(coord, player.personal_supply.take(component_type = cp.Dreadnought))
            
            for cube_slot in self.board.get_components(coord, zn.ResourceSlot):
                if cube_slot.isAllowed(player):
                    cube_slot.add(player.personal_board.population_track.take(cube_slot.resource_type))
            
    def get_current_round(self):
        return len(self.rounds)
    
    def next_player(self):
        """Return a generator iterating over the players."""
        n = 0
        n_players = len(self.players)
        while(True):
            yield self.players[n % n_players]
            n += 1

    def end_turn(self, passing = False):
        """End of an action turn. The current player is updated."""
        self.current_player = self.player_iterator.next()
    
    def move(self, zone_from = None, zone_to = None, component = None, component_type = None, resource_type = None):
        """
        Move a component (influence disc, ships, hex, population cube). Destination
        is hex coordinates (tuple)
        """
        if zone_from is None:
            zone_from = self.board
        if zone_to is None:
            zone_to = self.board
        if component is None:
            component = zone_from.take(component_type = component_type, resource_type = resource_type)
        else:
            zone_from.take(component_type = component_type, resource_type = resource_type)
        zone_to.add(component, resource_type = resource_type)

    def get_coord_ring(self, coord):
        abs_half_x = (abs(coord[0]) + 1)//2
        abs_coord = (abs_half_x, abs(coord[1]))
        ring = min(max(abs_coord), 3)
        if (abs_coord == (2, 2)):
            ring += 1
        return ring
            
            
        
    def draw_hex(self, coord):
        """
        Method called when a player is exploring. Return a SectorTile object
        from the draw pile corresponding to the coordinates. Return None
        if the draw pile was empty."""
        draw_pile_number = self.get_coord_ring(coord)

        draw_pile = [self.inner_sectors_drawpile,
                     self.middle_sectors_drawpile,
                     self.outer_sectors_drawpile
                     ][draw_pile_number - 1]
        return draw_pile.draw()
    
    def place_hex(self, sector_tile, coord):
        """
        Place a SectorTile on the board.
        """
        return self.board.add(coord, sector_tile)   
        
    def rotate_hex(self, coord, amount = 1):
        sector = self.board.get_components(coord, Sector)
        sector.rotate(n = amount)
        
class Phase(object):
    pass
    
class ActionPhase(Phase):
    pass

class CombatPhase(Phase):
    pass

class UpkeepPhase(Phase):
    pass

class CleanupPhase(Phase):
    pass
