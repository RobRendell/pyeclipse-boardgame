from engine.component import SectorTile
import csv

__author__="jglouis"
__date__ ="$Dec 21, 2011 3:31:15 PM$"


#this module generates three lists of sector types + the GCDS in a separate variable
galactic_center = []
inner_hexes = []
middle_hexes = []
outer_hexes = []
starting_hexes = []

def create_sector_tile(row):
    return SectorTile(
        row[0],
        row[1],
        int(row[2]),
        int(row[3]),
        int(row[4]),
        int(row[5]),
        int(row[6]),
        int(row[7]),
        int(row[8]),
        int(row[9]),
        int(row[10]),
        int(row[11]),
        int(row[12]),
        int(row[13]),
        int(row[14]),
        int(row[15]),
        int(row[16]),
        int(row[17]),
        int(row[18])
    )

reader = csv.reader(open('data/sectortiles.csv'), delimiter = ';')

#skip the first line
reader.next()

for row in reader:
    if row[0][0] == '0':
        galactic_center.append(create_sector_tile(row))
    elif row[0][0] == '1':
        inner_hexes.append(create_sector_tile(row))
    elif row[0][0] == '2':
        if '221' <= row[0] <= '232':
            starting_hexes.append(create_sector_tile(row))
        else:
            middle_hexes.append(create_sector_tile(row))
    elif row[0][0] == '3':
        outer_hexes.append(create_sector_tile(row))


print len(galactic_center), 'gc loaded...'
print len(inner_hexes), 'inner sector tiles loaded...'
print len(middle_hexes), 'middle sector tiles loaded...'
print len(outer_hexes), 'outer sector tiles loaded...'
print len(starting_hexes), 'starting sector tiles loaded...'