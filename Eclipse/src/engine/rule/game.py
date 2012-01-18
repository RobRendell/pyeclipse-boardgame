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

__author__="jglouis"
__date__ ="$Dec 22, 2011 5:56:29 PM$"

class GameSlice(object):
    def __init__(self, game_slices = [], *args):
        self.sub_slices = game_slices + list(args)
        self.slice_iterator = iter(self.sub_slices)

    def do(self):
        """Execute the current slice. Return True if the slice is finished."""
        try:
            self.slice_iterator.next().do()
        except:
            return True

class Game(GameSlice):
    def __init__(self, n_players):
        super(Game, self).__init__([Round() for n in range(1,10)])
        #creating the players
        factions = fa.factions
        self.players = []
        for dummy in range(n_players):
            rand_faction = random.choice(factions)
            factions = [faction for faction in factions if faction.color != rand_faction.color]
            self.players.append(pl.Player(rand_faction))

        #setting the ship part tiles reserver
        self.ship_parts_supply = zn.ShipPartsTilesSupply(sp.ship_parts)

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

        #choose a first player
        self.first_player = random.choice(self.players)
        self.current_player = self.first_player
        
        #assign a personal board, a starting hex and a personal supply to each player
        for n, player in enumerate(self.players):
            player.personal_board = cp.PlayerBoard(player, self.ship_parts_supply)
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
            elif n_players == 3:
                coord = [(2,2),(0,-2),(-2,0)][n]  
            elif n_players == 4:
                coord =[(2,2),(0,-2),(-2,-2),(0,2)][n]
            elif n_players == 5:
                coord = [(2,2),(2,0),(0,-2),(-2,-2),(-2,0)][n]  
            elif n_players == 6:
                coord = [(2,2),(2,0),(0,-2),(-2,-2),(-2,0),(0,2)][n]              
            self.board.add(coord, player.starting_hex)
            self.board.add(coord, player.personal_board.influence_track.take())
            self.board.add(coord, player.personal_supply.take(
                                                              component_type = {'interceptor' : cp.Interceptor,
                                                                                'cruiser' : cp.Cruiser                                                                              
                                                                                }[player.faction.starting_unit]
                                                              ))
            for cube_slot in self.board.get_content(coord, zn.ResourceSlot):
                if cube_slot.isAllowed(player):
                    cube_slot.add(player.personal_board.population_track.take(cube_slot.resource_type))
            
    def get_current_round(self):
        return len(self.rounds)
        
class Round(GameSlice):
    def __init__(self):
        super(Round, self).__init__(ActionPhase(),
                                    CombatPhase(),
                                    UpkeepPhase(),
                                    CleanupPhase()
                                    )
        
    def do(self):
        
        super(Round, self).do()
        
class Phase(GameSlice):
    pass
    
class ActionPhase(Phase):
    pass

class CombatPhase(Phase):
    pass

class UpkeepPhase(Phase):
    pass

class CleanupPhase(Phase):
    pass
        
class Step(GameSlice):
    """represents the smallest game slice division."""
    def __init__(self, action):
        """action may be an Action, Reaction, FreeAction, ForcedAction or GameAction"""
        super(Step, self).__init__()
        self.action = action
    
    def do(self):
        self.action.do()
        return True