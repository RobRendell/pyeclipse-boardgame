import unittest
from gui.play import FlowLayoutLayer, HudLayer
import mock
from mock import call

class TestFlowLayoutLayer(unittest.TestCase):
    
    @mock.patch('cocos.cocosnode.Camera')
    @mock.patch('cocos.layer.base_layers.director')
    def setUp(self, mockDirector, mockCamera):
        mockDirector.get_window_size.return_value = (640, 480)
        self.layer = FlowLayoutLayer()

    def test_add_box_will_remember_first_box(self):
        cursor = self.layer.add_box(10, 20)
        self.assertEqual((0, 0), cursor)
        self.assertEqual(1, len(self.layer.left_box))
        self.assertEqual(10, self.layer.left_box[-1][0])
        self.assertEqual(-20, self.layer.left_box[-1][1])

    def test_add_box_will_append_second_box_if_vertically_smaller(self):        
        self.layer.add_box(10, 20)
        cursor = self.layer.add_box(10, 10)
        self.assertEqual((10, 0), cursor)
        self.assertEqual(2, len(self.layer.left_box))
        self.assertEqual(20, self.layer.left_box[-1][0])
        self.assertEqual(-10, self.layer.left_box[-1][1])

    def test_add_box_will_replace_boxes_if_vertically_equal(self):
        self.layer.add_box(10, 20)
        cursor = self.layer.add_box(10, 20)
        self.assertEqual((10, 0), cursor)
        self.assertEqual(1, len(self.layer.left_box))
        self.assertEqual(20, self.layer.left_box[-1][0])
        self.assertEqual(-20, self.layer.left_box[-1][1])

    def test_add_box_will_replace_boxes_if_vertically_larger(self):
        self.layer.add_box(10, 20)
        self.layer.add_box(10, 19)
        self.layer.add_box(10, 18)
        cursor = self.layer.add_box(10, 30)
        self.assertEqual((30, 0), cursor)
        self.assertEqual(1, len(self.layer.left_box))
        self.assertEqual(40, self.layer.left_box[-1][0])
        self.assertEqual(-30, self.layer.left_box[-1][1])

    def test_add_box_will_CR_to_next_available_space_if_overflow_horizontal_room(self):
        self.layer.add_box(10, 40)
        self.layer.add_box(10, 10)
        cursor = self.layer.add_box(90, 20)
        self.assertEqual((10, -10), cursor)
        self.assertEqual(2, len(self.layer.left_box))
        self.assertEqual(100, self.layer.left_box[-1][0])
        self.assertEqual(-30, self.layer.left_box[-1][1])

    def test_add_box_will_CR_to_left_margin_if_overflow_horizontal_room_past_all_boxes(self):
        self.layer.add_box(10, 30)
        self.layer.add_box(10, 10)
        cursor = self.layer.add_box(100, 30)
        self.assertEqual((0, -30), cursor)
        self.assertEqual(1, len(self.layer.left_box))
        self.assertEqual(100, self.layer.left_box[-1][0])
        self.assertEqual(-60, self.layer.left_box[-1][1])

    def test_add_box_will_throw_if_not_enough_horizontal_room(self):
        with self.assertRaises(ValueError):
            self.layer.add_box(101, 30)

    def test_new_line_will_move_down_past_box(self):
        self.layer.add_box(10, 20)
        self.layer.new_line()
        self.assertEqual(-20, self.layer.cursor[1])
        self.assertEqual(0, len(self.layer.left_box))

    def test_new_line_will_move_down_past_box_plus_vspace(self):
        self.layer.add_box(10, 20)
        self.layer.new_line(vspace = 2)
        self.assertEqual(-22, self.layer.cursor[1])
        self.assertEqual(0, len(self.layer.left_box))
        self.assertEqual(0, len(self.layer.left_box))

    def test_new_line_will_move_down_past_multiple_boxes_with_enough_vspace(self):
        self.layer.add_box(10, 50)
        self.layer.add_box(10, 40)
        self.layer.add_box(10, 30)
        self.layer.new_line(vspace = 12)
        self.assertEqual(-42, self.layer.cursor[1])
        self.assertEqual(10, self.layer.cursor[0])
        self.assertEqual(1, len(self.layer.left_box))

    def test_new_line_will_move_down_past_all_boxes_if_clear_True(self):
        self.layer.add_box(10, 50)
        self.layer.add_box(10, 40)
        self.layer.add_box(10, 30)
        self.layer.new_line(clear = True)
        self.assertEqual(-50, self.layer.cursor[1])
        self.assertEqual(0, len(self.layer.left_box))
        self.assertEqual(0, len(self.layer.left_box))

    def test_new_line_will_move_down_past_all_boxes_plus_vspace_if_clear_True(self):
        self.layer.add_box(10, 50)
        self.layer.add_box(10, 40)
        self.layer.add_box(10, 30)
        self.layer.new_line(clear = True, vspace = 7)
        self.assertEqual(-57, self.layer.cursor[1])
        self.assertEqual(0, len(self.layer.left_box))
        self.assertEqual(0, len(self.layer.left_box))

class TestHudLayer(unittest.TestCase):
    
    @mock.patch('gui.play.MainScreen')
    @mock.patch('engine.rule.game.Game')
    @mock.patch('gui.play.FlowLayoutLayer')
    @mock.patch('cocos.cocosnode.Camera')
    @mock.patch('cocos.layer.base_layers.director')
    @mock.patch('gui.play.director')
    def setUp(self, director, base_layers_director, camera, flow_layer, game, main_screen):
        director.get_window_size.return_value = (640, 480)
        base_layers_director.get_window_size.return_value = (640, 480)
        self.hud = HudLayer(game, main_screen)
        
    def test_draw_ship_system_info_will_add_single_image_if_unknown(self):
        self.hud.draw_ship_system_info('fnord', { 'fnord': 1 })
        self.hud.sub_layer.add_image.assert_called_with('ship_stats/fnord.png', scale = 0.9)

    def test_draw_ship_system_info_will_add_numbered_image_if_known_numbered(self):
        self.hud.draw_ship_system_info('computer', { 'computer': 4 })
        self.hud.sub_layer.add_image.assert_called_with('ship_stats/computer_4.png', scale = 0.9)

    def test_draw_ship_system_info_will_add_several_numbered_image_if_known_numbered_and_more_than_max(self):
        self.hud.draw_ship_system_info('computer', { 'computer': 7 })
        self.hud.sub_layer.add_image.assert_has_calls([ call('ship_stats/computer_5.png', scale = 0.9),
                                                      call('ship_stats/computer_2.png', scale = 0.9) ])
