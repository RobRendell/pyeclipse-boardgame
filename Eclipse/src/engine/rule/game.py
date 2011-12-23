import random
from engine.component import TraitorCard
from engine.rule.player import Player
from engine.zone import Bag
from engine.zone import Board
from engine.zone import DrawPile
from engine.zone import ShipPartsTilesSupply
import material.discoverytiles as dt
import material.reputationtiles as rt
import material.sectortiles as st
import material.shipparts as sp
import material.technologytiles as tt
import material.factions as f

__author__="jglouis"
__date__ ="$Dec 22, 2011 5:56:29 PM$"

class Game(object):
    def __init__(self, n_players):
        #creating the players
        factions = f.factions
        self.players = []
        for dummy in range(n_players):
            rand_faction = random.choice(factions)
            factions = [faction for faction in factions if faction.color != rand_faction.color]
            self.players.append(Player(rand_faction))
        print [p.faction.color for p in self.players]

        #setting the ship part tiles reserver
        self.ship_parts_supply = ShipPartsTilesSupply(sp.ship_parts)

        #game log
        self.rounds = []

        #create the bag of technology tiles
        self.technology_tiles_bag = Bag(tt.technology_tiles)

        #create the bag of reputation tiles
        self.reputations_tiles_bag = Bag(rt.reputation_tiles)

        #create the pile of discovery tiles
        self.discovery_tiles_draw_pile = DrawPile(dt.discovery_tiles)

        #create a traitor card
        self.traitor_card = TraitorCard()

        #create the board
        self.board = Board(self)

        #add the galactic center
        self.board.add((0,0), st.galactic_center[0])

        #create the 3 drawpiles for the sectors
        self.inner_sectors_drawpile = DrawPile(st.inner_hexes)
        self.middle_sectors_drawpile = DrawPile(st.middle_hexes)
        self.outer_sectors_drawpile = DrawPile(st.outer_hexes)

        #choose a first player
        self.first_player = random.choice(self.players)