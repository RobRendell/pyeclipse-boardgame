'''
Created on 9 janv. 2012

@author: jglouis
'''
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
    
if __name__ == "__main__":
    hm = HexManager(20.0)
    u, v = hm.get_hex_from_rect_coord(21, 0)
    print hm.get_rect_coord_from_hex_coord(u, v)
    
    