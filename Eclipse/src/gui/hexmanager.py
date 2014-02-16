'''
Created on 9 janv. 2012

@author: jglouis
'''
import random
import math

class HexManager(object):
    def __init__(self, hex_width, center_rect_coord = (0,0)):
        """
        Create a hexagonal grid manager for vertex-up hexes.
        hex_width is the euclidian distance between two edges (small radius).
        center_rect_coord sets the specified rectangular coordinates of the window
        as the origin of the hex axes system.
        """
        self.hex_width = float(hex_width)
        self.hex_height = 2 * self.hex_width / math.sqrt(3)
        self.hex_height34 = self.hex_height * 3 / 4
        self.x_offset = center_rect_coord[0]
        self.y_offset = center_rect_coord[1]
        self.sprite_slots = {} #relative hex coord -> sprite
        
    def get_hex_from_hex_coord(self, u, v):
        """get the hexagon coordinates containing the point (u,v)"""
        hex_u = int(math.floor(u))
        hex_v = int(math.floor(v))
        legal = (hex_u & 1) == (hex_v & 1)
        row = 3*(v - hex_v)
        if (legal and row > 2 + hex_u - u) or (not legal and row > 1 + u - hex_u):
            hex_v += 1
            legal = not legal
        if not legal:
            hex_u += 1
        return (hex_u, hex_v)
    
    def get_hex_from_rect_coord(self, x, y):
        """get the hexagon coordinates containing the point (x,y)"""
        u, v = self.get_hex_coord_from_rect_coord(x, y)
        return self.get_hex_from_hex_coord(u, v)
        
    def get_hex_coord_from_rect_coord(self, x, y):
        x -= self.x_offset
        y -= self.y_offset
        u = 2 * x / self.hex_width
        v = y / self.hex_height34
        return (u, v)
    
    def get_rect_coord_from_hex_coord(self, u, v):
        x, y = self.get_rect_coord_from_hex_coord(u, v)
        x += self.x_offset
        y += self.y_offset
        return (x, y)
    
    def get_rel_rect_coord_from_hex_coord(self, u, v):
        x = self.hex_width * u / 2
        y = self.hex_height34 * v
        return (x, y)
    
    def get_sprite_coord(self, u, v):
        """ get the rect coordinate to place a sprite"""
        slots = [(u + 0.3, v + 0.3),
                 (u + 0.6, v),
                 (u + 0.3, v - 0.3),
                 (u - 0.3, v - 0.3),
                 (u - 0.6, v),
                 (u - 0.3, v + 0.3)
                 ]
        random.shuffle(slots)
        for hex_coord in slots:
            if hex_coord not in self.sprite_slots :
                self.sprite_slots[hex_coord] = 'Occupied'
                u, v = hex_coord
                return self.get_rect_coord_from_hex_coord(u, v)
        
    
if __name__ == "__main__":
    hm = HexManager(20.0)
    u, v = hm.get_hex_from_rect_coord(21, 0)
    print hm.get_rect_coord_from_hex_coord(u, v)
    
    