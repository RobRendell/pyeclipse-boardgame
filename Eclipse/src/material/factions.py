from engine.rule.faction import Faction
from engine.component import TechnologyTile
import os.path
import csv

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

def create_faction(row):
    return Faction(
        row[0],
        row[1],
        int(row[2]),
        int(row[3]),
        int(row[4]),
        int(row[5]),
        int(row[6]),
        int(row[7]),
        row[8],
        int(row[9]),
        int(row[10]),
        int(row[11]),
        int(row[12]),
        int(row[13]),
        int(row[14]),
        create_starting_technology_tiles(row[15]),
        create_starting_technology_tiles(row[16]),
        create_starting_technology_tiles(row[17]),
        row[18],
        row[19],
        int(row[20]),
        int(row[21]),
        int(row[22]),
        int(row[23]),
        row[24]
    )

reader = csv.reader(open('data\\factions.csv'), delimiter = ';')

#skip the first line
reader.next()

for row in reader:
    factions.append(create_faction(row))

print len(factions), 'factions loaded...'