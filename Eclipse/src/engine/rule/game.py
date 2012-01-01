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

class Game(object):
    def __init__(self, n_players):
        #creating the players
        factions = fa.factions
        self.players = []
        for dummy in range(n_players):
            rand_faction = random.choice(factions)
            factions = [faction for faction in factions if faction.color != rand_faction.color]
            self.players.append(pl.Player(rand_faction))
        print [p.faction.color for p in self.players]

        #setting the ship part tiles reserver
        self.ship_parts_supply = zn.ShipPartsTilesSupply(sp.ship_parts)

        #game log
        self.rounds = []

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
        for player in self.players:
            player.personal_board = cp.PlayerBoard(player, self.ship_parts_supply)
            player.starting_hex = dict([(h.id, h) for h in st.starting_hexes])[player.faction.sector]
            player.personal_supply = zn.PersonalSupply(player)
            for dummy in range(8):   
                player.personal_supply.add(cp.Ship(player, 'interceptor'))
            for dummy in range(4):
                player.personal_supply.add(cp.Ship(player, 'cruiser'))
            for dummy in range(2):
                player.personal_supply.add(cp.Ship(player, 'dreadnought'))
            for dummy in range(4):
                player.personal_supply.add(cp.Ship(player, 'starbase'))
            for dummy in range(3):
                player.personal_supply.add(cp.AmbassadorTile(player))
            for dummy in range(player.faction.colony_ships):
                player.personal_supply.add(cp.ColonyShip(player))
            for dummy in range(player.faction.starting_influence):
                player.personal_board.influence_track.add(cp.InfluenceDisc(player))
            for resource in ['money', 'science', 'material']:
                for dummy in range(11):
                    player.personal_board.population_track.add(resource, cp.PopulationCube(player))
                   
    def get_current_round(self):
        return len(self.rounds)