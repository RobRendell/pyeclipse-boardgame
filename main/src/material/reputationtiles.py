from engine.component import ReputationTile

__author__="jglouis"
__date__ ="$Dec 22, 2011 4:13:17 PM$"

reputation_tiles = []

for dummy in range(8):
    for n in range(1,5):
        reputation_tiles.append(ReputationTile(n))

print len(reputation_tiles), 'reputation tiles created...'