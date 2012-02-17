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
        self.l = hex_width
        self.L = 2 * self.l / math.sqrt(3)
        self.x_offset = center_rect_coord[0]
        self.y_offset = center_rect_coord[1]
        self.sprite_slots = {} #relative hex coord -> sprite
        
    def get_hex_from_hex_coord(self, u, v):
        """get the hexagon coordinates containing the point (u,v)"""
        #approx               
        hex_u = int(u + math.copysign(0.5, u))
        hex_v = int(v + math.copysign(0.5, v))
        
        """if  u - hex_u + v - hex_v >  0.5:
            hex_u += 1
            hex_v += 1
        elif u - hex_u + v - hex_v < - 0.5:
            hex_u -= 1
            hex_v -= 1"""
        return (hex_u, hex_v)
    
    def get_hex_from_rect_coord(self, x, y):
        """get the hexagon coordinates containing the point (x,y)"""
        u, v = self.get_hex_coord_from_rect_coord(x, y)
        return self.get_hex_from_hex_coord(u, v)
        
    def get_hex_coord_from_rect_coord(self, x, y):
        x -= self.x_offset
        y -= self.y_offset
        u = 1.0 / self.l * x + 2.0 / ( 3.0 * self.L) * y
        v = 4.0 / (3.0 * self.L) * y
        return (u, v)
    
    def get_rect_coord_from_hex_coord(self, u, v):
        x = self.l * u - self.l / 2.0 * v
        y = 3.0 * self.L / 4.0 * v
        x += self.x_offset
        y += self.y_offset
        return (x, y)
    
    def get_planets_coord(self, u, v):
        """ get the rect coordinates to place planets as a list"""
        coords = []
        for n in range(3):
            su = [0.25, -0.25, 0][n]
            sv=  [0, -0.25, 0.25][n]
            su += u
            sv += v
            sx, sy = self.get_rect_coord_from_hex_coord(su, sv)
            coords.append((sx, sy))
        return coords
    
    def get_fleet_coord(self, u, v):
        """ get the rect coordinate to place ships"""
        sx, sy = self.get_rect_coord_from_hex_coord(0.25 + u, 0.25 + v)
        return (sx, sy)
    
    def get_sprite_coord(self, u, v):
        """ get the rect coordinate to place a sprite"""
        slots = [(u + 0.25, v + 0.25),
                 (u + 0.25, v),
                 (u, v - 0.25),
                 (u - 0.25, v - 0.25),
                 (u - 0.25, v),
                 (u, v + 0.25)
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
    
    