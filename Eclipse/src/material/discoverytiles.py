from engine.component import DiscoveryTile
import csv

__author__="jglouis"
__date__ ="$Dec 22, 2011 5:09:31 PM$"


discovery_tiles = []

def create_discovery_tile(row):
    return DiscoveryTile(
        row[1],
        int(row[2]),
        int(row[3]),
        int(row[4]),
        row[5],
        int(row[6]),
        int(row[7]),
        int(row[8]),
        int(row[9]),
        int(row[10]),
        bool(row[11]),
        int(row[12]),
        int(row[13]),
        int(row[14]),
        int(row[15])
    )

reader = csv.reader(open('data\\discoverytiles.csv'), delimiter = ';')

#skip the first line
reader.next()

for row in reader:
    for dummy in range(int(row[0])):
        discovery_tiles.append(create_discovery_tile(row))

print len(discovery_tiles), 'discovery tiles loaded...'