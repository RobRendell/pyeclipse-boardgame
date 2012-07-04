import os.path
from engine.component import ShipPartTile
import csv

__author__="jglouis"
__date__ ="$Dec 22, 2011 1:55:59 PM$"

ship_parts = []

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
        int(row[10]),
        int(row[11])
    )

reader = csv.reader(open('data/shipparts.csv'), delimiter = ';')

#skip the first line
reader.next()

for row in reader:
    ship_parts.append(create_ship_part_tile(row))

print len(ship_parts), 'ship parts tile loaded...'