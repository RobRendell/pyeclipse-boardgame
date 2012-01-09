'''
Created on 9 janv. 2012

@author: jglouis
'''
import math

class HexManager(object):
    def __init__(self, hex_width):
        self.l = hex_width
        self.L = 2 * self.l / math.sqrt(3)
        
    def get_hex_from_hex_coord(self, u, v):
        """get the hexagon coordinates containing the point (u,v)"""
        #approx
        k = 0.5 * self.l        
        hex_u = int(u / self.l + k)
        hex_v = int(v / self.l + k)
        #hexagon center
        center_u = hex_u * self.l
        center_v = hex_v * self.l
        #print hex_u, hex_v
        #print center_u, center_v
        
        if  u - center_u + v - center_v >  k:
            hex_u += 1
            hex_v += 1
        elif u - center_u + v - center_v < - k:
            hex_u -= 1
            hex_v -= 1
        #return (hex_u, hex_v)
        return (center_u, center_v)
    
    def get_hex_from_rect_coord(self, x, y):
        """get the hexagon coordinates containing the point (x,y)"""
        u, v = self.get_hex_coord_from_rect(x, y)
        #print ('u:', u, ', v:', v)
        return self.get_hex_from_hex_coord(u, v)
        
    def get_hex_coord_from_rect(self, x, y):
        u = 1.0 / self.l * x + 2.0 / ( 3.0 * self.L) * y
        v = 4.0 / (3.0 * self.L) * y
        return (u, v)
    
    def get_rect_coord_from_hex(self, u, v):
        x = self.l * u - self.l / 2.0 * v
        y = 3.0 * self.L / 4.0 * v
        return (x, y)
    
if __name__ == "__main__":
    hm = HexManager(1.0)
    print hm.get_hex_from_rect_coord(783, 740)
    u, v = hm.get_hex_from_rect_coord(783, 740)
    print hm.get_rect_coord_from_hex(u, v)
    
    u, v = hm.get_hex_coord_from_rect(100, 200)
    print hm.get_rect_coord_from_hex(u, v)