from engine.rule.action import Explore1
from cocos.actions.interval_actions import Rotate
from pyglet.window.mouse import LEFT
from engine.zone import Sector
from engine.component import InfluenceDisc, AncientShip

class GuiAction(object):
    """
    Each GuiAction object controls the UI to carry out a single user interaction, corresponding with
    the values in UIAction.
    """
    sprites_key = 'sprites'
    highlight_key = 'highlight hex'
    highlight_coords_key = 'highlight coords'
    
    def __init__(self, game, main_screen):
        self.game = game
        self.main_screen = main_screen
    
    def on_start(self):
        pass
    
    def on_end(self):
        action_state = self.main_screen.action_state
        if self.sprites_key in action_state:
            for sprite in action_state[self.sprites_key]:
                sprite.kill()
            del action_state[self.sprites_key]
        self.remove_highlight_hex()
    
    def is_finished(self):
        return True
    
    def on_hex_mouse_move(self, coords):
        pass
    
    def on_hex_mouse_click(self, coords, button, modifiers):
        pass
    
    def get_influence_disc_drop_target(self):
        return None

    def remove_highlight_hex(self):
        action_state = self.main_screen.action_state
        if self.highlight_key in action_state:
            for sprite in action_state[self.highlight_key]:
                sprite.kill()
            del action_state[self.highlight_key]
            del action_state[self.highlight_coords_key]

    def update_highlight_hex(self, coords):
        action_state = self.main_screen.action_state
        if self.highlight_coords_key not in action_state:
            action_state[self.highlight_coords_key] = None
        if action_state[self.highlight_coords_key] != coords:
            self.remove_highlight_hex()
            action_state[self.highlight_coords_key] = coords
            if coords is not None:
                sprites = self.main_screen.board_scene.board_layer.draw_hex_outline(coords, z = 4)
                self.main_screen.action_state[self.highlight_key] = sprites

class ShowSceneGuiAction(GuiAction):
    def __init__(self, game, main_screen, scene):
        super(ShowSceneGuiAction, self).__init__(game, main_screen)
        self.scene = scene
        
    def on_start(self):
        self.main_screen.transition(self.scene)

class SelectUnexploredHexGuiAction(GuiAction):
    def on_start(self):
        action_state = self.main_screen.action_state
        sprites = self.main_screen.board_scene.highlight_hexes(action_state[Explore1.unexplored_key])
        action_state[self.sprites_key] = sprites

    def is_finished(self):
        return Explore1.selected_key in self.main_screen.action_state

    def on_hex_mouse_move(self, coords):
        if coords in self.main_screen.action_state[Explore1.unexplored_key]:
            self.update_highlight_hex(coords)
            return True
        else:
            self.update_highlight_hex(None)

    def on_hex_mouse_click(self, coords, button, modifiers):
        if self.on_hex_mouse_move(coords):
            self.main_screen.action_state[Explore1.selected_key] = coords
            return True

class SelectFromHexGuiAction(GuiAction):
    def on_start(self):
        if not self.is_finished():
            action_state = self.main_screen.action_state
            sprites = self.main_screen.board_scene.highlight_hexes(action_state[Explore1.from_hex_key])
            sprites.extend(self.main_screen.board_scene.highlight_hexes([ action_state[Explore1.selected_key] ]))
            action_state[self.sprites_key] = sprites
            self.main_screen.board_scene.hud_layer.set_info('Explore hex from which direction?')
    
    def is_finished(self):
        return len(self.main_screen.action_state[Explore1.from_hex_key]) == 1

    def on_hex_mouse_move(self, coords):
        if coords in self.main_screen.action_state[Explore1.from_hex_key]:
            self.update_highlight_hex(coords)
            return True
        else:
            self.update_highlight_hex(None)

    def on_hex_mouse_click(self, coords, button, modifiers):
        if self.on_hex_mouse_move(coords):
            self.main_screen.action_state[Explore1.from_hex_key] = [ coords ]
            return True

class RotateRejectGuiAction(GuiAction):
    def on_start(self):
        coord = self.main_screen.action_state[Explore1.selected_key]
        self.main_screen.board_scene.board_layer.display_sector(coord)

    def is_finished(self):
        return False
    
    def on_hex_mouse_click(self, coords, button, modifiers):
        action_state = self.main_screen.action_state
        if button == LEFT and coords == action_state[Explore1.selected_key]:
            if not self.main_screen.board_scene.board_layer.is_hex_rotating(coords):
                sector = self.game.board.get_components(coords)[0]
                sector.rotate()
                rotate = 1
                while not self.game.board.has_wormhole_connection(action_state[Explore1.from_hex_key][0], coords, self.game.current_player):
                    sector.rotate()
                    rotate += 1
                self.main_screen.board_scene.board_layer.rotate_hex(coords, rotate)

    def get_influence_disc_drop_target(self):
        selected = self.main_screen.action_state[Explore1.selected_key]
        sector = self.game.board.get_components(selected, Sector)
        if len(sector.get_components(component_type = InfluenceDisc)) == 0 and len(sector.get_components(component_type = AncientShip)) == 0:
            return selected
        else:
            return None

class ShowCurrentPlayerBoardGuiAction(GuiAction):
    def on_start(self):
        self.main_screen.show_current_player_board()

