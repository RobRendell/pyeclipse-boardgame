from engine.rule.game import Game
import unittest

class TestGame(unittest.TestCase):
    
    def setUp(self):
        self.game = Game(2)
    
    def assert_ring(self, coord, expected):
        ring = self.game.get_coord_ring(coord)
        self.assertEqual(expected, ring, str(coord) + " should be in ring " + str(expected) + ", actual " + str(ring))
    
    def test_get_coord_ring_0(self):
        self.assert_ring((0, 0), 0)

    def test_get_coord_ring_1(self):
        self.assert_ring((1, 1), 1)
        self.assert_ring((2, 0), 1)
        self.assert_ring((1, -1), 1)
        self.assert_ring((-1, 1), 1)
        self.assert_ring((-2, 0), 1)
        self.assert_ring((-1, -1), 1)
        
    def test_get_coord_ring_2(self):
        self.assert_ring((0, 2), 2)
        self.assert_ring((2, 2), 2)
        self.assert_ring((3, 1), 2)
        self.assert_ring((4, 0), 2)
        self.assert_ring((3, -1), 2)
        self.assert_ring((2, -2), 2)
        self.assert_ring((0, -2), 2)
        self.assert_ring((-2, 2), 2)
        self.assert_ring((-3, 1), 2)
        self.assert_ring((-4, 0), 2)
        self.assert_ring((-3, -1), 2)
        self.assert_ring((-2, -2), 2)
        
    def test_get_coord_ring_3(self):
        self.assert_ring((1, 3), 3)
        self.assert_ring((3, 3), 3)
        self.assert_ring((4, 2), 3)
        self.assert_ring((5, 1), 3)
        self.assert_ring((6, 0), 3)
        self.assert_ring((5, -1), 3)
        self.assert_ring((4, -2), 3)
        self.assert_ring((3, -3), 3)
        self.assert_ring((1, -3), 3)
        self.assert_ring((-1, 3), 3)
        self.assert_ring((-3, 3), 3)
        self.assert_ring((-4, 2), 3)
        self.assert_ring((-5, 1), 3)
        self.assert_ring((-6, 0), 3)
        self.assert_ring((-5, -1), 3)
        self.assert_ring((-4, -2), 3)
        self.assert_ring((-3, -3), 3)
        self.assert_ring((-1, -3), 3)
