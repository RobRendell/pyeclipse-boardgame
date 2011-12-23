__author__="jglouis"
__date__ ="$Dec 23, 2011 1:16:52 PM$"

class Faction(object):
    def __init__(self, name, color, explore, research,  upgrade, build, move,
    trade, sector, reputation_diplomacy, reputation_only, diplomacy_only,
    starting_money, starting_science, starting_material, tech1, tech2, tech3,
    starting_unit, vp_bonus, colony_ships, starting_reputation,
    starting_influence, ship_cost_reduction, special):
        self.name = name
        self.color = color
        self.explore = explore
        self.research = research
        self.upgrade = upgrade
        self.build = build
        self.move = move
        self.trade = trade
        self.sector = sector
        self.reputation_diplomacy = reputation_diplomacy
        self.reputation_only = reputation_only
        self.diplomacy_only = diplomacy_only
        self.starting_money = starting_money
        self.starting_science = starting_science
        self.starting_material = starting_material
        self.tech1 = tech1
        self.tech2 = tech2
        self.tech3 = tech3
        self.starting_unit = starting_unit
        self.vp_bonus = vp_bonus
        self.colony_ships = colony_ships
        self.starting_reputation = starting_reputation
        self.starting_influence = starting_influence
        self.ship_cost_reduction = ship_cost_reduction
        self.special = special

        self.starting_technologies = []
        if self.tech1:
            self.starting_technologies.append(self.tech1)
        if self.tech2:
            self.starting_technologies.append(self.tech2)
        if self.tech3:
            self.starting_technologies.append(self.tech3)