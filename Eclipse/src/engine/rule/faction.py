__author__="jglouis"
__date__ ="$Dec 23, 2011 1:16:52 PM$"

class Faction(object):
    def __init__(self, name, color, board, actions, trade, sector,
                 reputation_diplomacy, reputation_only, diplomacy_only,
                 starting_money, starting_science, starting_material, starting_techs,
                 starting_unit, colony_ships, starting_reputation, starting_influence,
                 blueprints, special):
        self.name = name
        self.color = color
        self.board = board
        self.actions = actions
        self.trade = trade
        self.sector = sector
        self.reputation_diplomacy = reputation_diplomacy
        self.reputation_only = reputation_only
        self.diplomacy_only = diplomacy_only
        self.starting_money = starting_money
        self.starting_science = starting_science
        self.starting_material = starting_material
        self.starting_technologies = starting_techs
        self.starting_unit = starting_unit
        self.colony_ships = colony_ships
        self.starting_reputation = starting_reputation
        self.starting_influence = starting_influence
        self.blueprints = blueprints
        self.special = special
