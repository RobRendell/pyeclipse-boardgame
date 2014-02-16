
import json
import os

from engine.rule.faction import Faction
from material.technologytiles import technology_tile_type


__author__="jglouis"
__date__ ="$Dec 23, 2011 11:33:19 AM$"

factions = []

def create_faction_json(json):
    starting_technologies = []
    for tech in json["starting_techs"]:
        starting_technologies.append(technology_tile_type[tech])
    return Faction(
        json["name"],
        json["color"],
        json['board'],
        json["actions"],
        json["trade"],
        str(json["sector"]),
        json["reputation_diplomacy"],
        json["reputation_only"],
        json["diplomacy_only"],
        json["starting_money"],
        json["starting_science"],
        json["starting_material"],
        starting_technologies,
        json["starting_units"][0],
        json["colony_ships"],
        json["starting_reputation"],
        json["starting_influence"],
        json["blueprints"],
        json["special"] if "special" in json else None
    )

for faction_file in os.listdir('data/factions/'):
    faction_json = json.load(open('data/factions/' + faction_file))
    factions.append(create_faction_json(faction_json))

print len(factions), 'factions loaded...'
