from engine.component import TechnologyTile
import csv
import os.path

__author__="jglouis"
__date__ ="$Dec 22, 2011 11:42:36 AM$"

technology_tiles = []

def create_technology_tile(row):
    return TechnologyTile(
        row[0],
        int(row[1]),
        int(row[2]),
        row[3],
        row[4]
    )

reader = csv.reader(open('data/technologytiles.csv'), delimiter = ';')

#skip the first line
reader.next()

for row in reader:
    for dummy in range(int(row[5])):
        technology_tiles.append(create_technology_tile(row))