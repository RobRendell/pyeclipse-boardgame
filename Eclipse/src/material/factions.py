from engine.rule.faction import Faction
from engine.component import TechnologyTile
import os
import csv
import json

__author__="jglouis"
__date__ ="$Dec 23, 2011 11:33:19 AM$"

factions = []

def create_starting_technology_tiles(name):
    reader = csv.reader(open('data/technologytiles.csv'), delimiter = ';')
    for row in reader:
        if row[0] == name:
            return TechnologyTile(
                        row[0],
                        int(row[1]),
                        int(row[2]),
                        row[3],
                        row[4]
                    )

def create_faction_json(json):
    starting_technologies = []
    for tech in json["starting_techs"]:
        starting_technologies.append(create_starting_technology_tiles(tech.lower()))
    return Faction(
        json["name"].lower(),
        str(json["color"]),
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
        json["special"] if json.has_key("special") else None
    )

for faction_file in os.listdir('data/factions/'):
    print faction_file
    faction_json = json.load(open('data/factions/' + faction_file))
    factions.append(create_faction_json(faction_json))


print len(factions), 'factions loaded...'
