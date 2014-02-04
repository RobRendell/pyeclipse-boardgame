import csv

from engine.component import ShipPartTile


__author__="jglouis"
__date__ ="$Dec 22, 2011 1:55:59 PM$"

ship_parts = {}

def create_ship_part_tile(row):
    return ShipPartTile(
        row[0],
        bool(row[1]),
        int(row[2]),
        int(row[3]),
        int(row[4]),
        int(row[5]),
        int(row[6]),
        row[7] == 'True',
        int(row[8]),
        int(row[9]),
        int(row[10])
    )

def load_ship_part_file(file_name):
    reader = csv.reader(open(file_name), delimiter = ';')
    #skip the first line
    reader.next()
    for row in reader:
        tile = create_ship_part_tile(row)
        ship_parts[tile.name] = tile
    print len(ship_parts), 'ship parts tile loaded...'

load_ship_part_file('data/shipparts.csv')

