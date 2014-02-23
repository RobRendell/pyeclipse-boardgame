from engine.component import TechnologyTile
import csv

__author__="jglouis"
__date__ ="$Dec 22, 2011 11:42:36 AM$"

technology_tile_type = {}
technology_tiles = []

def create_technology_tile(row):
    return TechnologyTile(
        row[0],
        int(row[1]),
        int(row[2]),
        row[3],
        row[4]
    )

def load_technology_tile_file(file_name):
    reader = csv.reader(open(file_name), delimiter = ';')
    #skip the first line
    reader.next()
    for row in reader:
        tech = create_technology_tile(row)
        technology_tile_type[tech.name] = tech
        for dummy in range(int(row[5])):
            technology_tiles.append(tech)
            
load_technology_tile_file('data/technologytiles.csv')