'''
Created on 4 janv. 2012

@author: jglouis
'''
import math
import random

from cocos.actions.base_actions import IntervalAction
from cocos.actions.interval_actions import Rotate, MoveTo
from cocos.director import director
from cocos.draw import Line
from cocos.layer.base_layers import Layer
from cocos.layer.scrolling import ScrollableLayer, ScrollingManager
from cocos.layer.util_layers import ColorLayer
from cocos.menu import Menu, MenuItem, LEFT, BOTTOM, verticalMenuLayout
from cocos.rect import Rect
from cocos.scene import Scene
from cocos.scenes.transitions import FadeUpTransition, ZoomTransition
from cocos.sprite import Sprite
from cocos.text import Label
import pyglet
from pyglet.event import EVENT_HANDLED
from pyglet.gl.gl import glViewport, glMatrixMode, glLoadIdentity, GL_PROJECTION, \
    GL_MODELVIEW, glOrtho
from pyglet.window.key import B, R, _1, P, MOD_CTRL
from pyglet.window.mouse import RIGHT

from engine.component import InfluenceDisc, Ship, Interceptor, Cruiser, \
    Dreadnought, Starbase, AncientShip, GalacticCenterDefenseSystem, DiscoveryTile
from engine.rule.action import actions, UIAction
from engine.zone import Sector, ResourceSlot, ActionBoard
from hexmanager import HexManager
from gui.guiaction import ShowSceneGuiAction, SelectUnexploredHexGuiAction,\
    SelectFromHexGuiAction, RotateRejectGuiAction,\
    ShowCurrentPlayerBoardGuiAction

pyglet.resource.path.append('./image')
pyglet.resource.path.append('./image/boards')
pyglet.resource.path.append('./image/diplomats')
pyglet.resource.path.append('./image/discovery_tiles')
pyglet.resource.path.append('./image/upgrade_tiles')
pyglet.resource.path.append('./image/research_tiles')
pyglet.resource.path.append('./image/npc')
pyglet.resource.path.append('./image/ships')
pyglet.resource.path.append('./font')
pyglet.resource.path.append('./ship_stats')
pyglet.resource.reindex()

pyglet.font.add_directory('font')
    
def color_convert(text):
    return {'white'     :(255, 255, 255),
            'red'       :(255, 0, 0),
            'green'     :(0, 255, 0),
            'blue'      :(0, 0, 255),
            'yellow'    :(255, 255, 0),
            'grey'      :(150, 150, 150),
            'black'     :(50, 50, 50),
            'money'     :(212, 100, 4),
            'material'  :(136, 72, 41),
            'science'   :(230, 146, 161),
            None        :(255, 255, 255)
            }[text]

def decorator(f):
    def new_f(self):
        if len(self.resource_slot_sprite.obj.get_components()) == 1:  # remove population cube                
            cube = self.resource_slot_sprite.obj.get_components()[0]
            self.game.move(self.resource_slot_sprite.obj, cube.owner.personal_board.population_track, resource_type = f(self))
            self.resource_slot_sprite.remove(self.resource_slot_sprite.get_children()[0])             
        else:          
            self.game.move(self.player.personal_board.population_track, self.resource_slot_sprite.obj, resource_type = f(self))
            color = color_convert(self.player.color)
            population_sprite = Sprite('population white.png',
                                                           position = self.resource_slot_sprite.position,
                                                           color = color,
                                                           scale = 0.2
                                                           )
            self.resource_slot_sprite.add(population_sprite, 1)       
        self.kill()      
    return new_f

def get_physical_dimensions(width, height):
    """
    Translate virtual width/height to physical dimensions
    """
    p_width = director._usable_width * width / director._window_virtual_width
    p_height = director._usable_height * height / director._window_virtual_height
    return (int(p_width), int(p_height))

def get_physical_coordinates(x, y):
    """
    Reverse operation to director.get_virtual_coordinates... why isn't this part of Director?
    """
    p_x, p_y = get_physical_dimensions(x, y)
    return (director._offset_x + p_x, director._offset_y + p_y)


def adjust_for_parents(ancestor):
    if ancestor.parent is not None:
        result = adjust_for_parents(ancestor.parent)
    else:
        result = (0, 0, 1.)
    return (result[0] + ancestor.x * result[2], result[1] + ancestor.y * result[2], ancestor.scale * result[2])


class SelectableSprite(Sprite):
    """
    A sprite that is linked to a zone/component of the game.
    The zone/component object is the obj variable of the sprite.
    """
    def __init__(self, obj, *args, **kwargs):
        super(SelectableSprite, self).__init__(*args, **kwargs)
        self.obj = obj
        
class PopUpSprite(Sprite):
    def __init__(self, game, board_layer, resource_slot_sprite, player):
        # extract all the selectable sprite from *args
        super(PopUpSprite, self).__init__('tech_background.png', anchor = (0, 0), scale = 2)
        
        self.add(PopulationChoiceMenu(game, board_layer, resource_slot_sprite, player))        
        
class BackgroundSprite(Sprite):
    pass

class AnchorSprite(Sprite):
    def __init__(self, image, anchor, rect = None, **kwargs):
        if isinstance(image, str) or isinstance(image, unicode):
            image = pyglet.resource.image(image)
        if rect is not None:
            image = image.get_region(rect.x, rect.y, rect.width, rect.height)
            pixel_anchor = (int(rect.width * anchor[0]), int(rect.height * anchor[1]))
        else:
            pixel_anchor = (int(image.width * anchor[0]), int(image.height * anchor[1]))
        super(AnchorSprite, self).__init__(image, anchor = pixel_anchor, **kwargs)

    def contains(self, x, y):
        adjust = adjust_for_parents(self.parent)
        x = (x - adjust[0]) / adjust[2]
        y = (y - adjust[1]) / adjust[2]
        sx, sy = self.position
        ax, ay = self.image_anchor
        sx -= ax * self.scale
        sy -= ay * self.scale
        if x < sx or x > sx + self.width: return False
        if y < sy or y > sy + self.height: return False
        return True

class ClipLayer(Layer):
    
    def __init__(self, clip_rect, position = (0, 0)):
        super(ClipLayer, self).__init__();
        self.position = position
        self.clip_rect = clip_rect
        
    def visit(self):
        phys_coord = get_physical_coordinates(self.position[0] + self.clip_rect.x, self.position[1] + self.clip_rect.y)
        phys_dimensions = get_physical_dimensions(self.clip_rect.width, self.clip_rect.height)
        pyglet.gl.glScissor(phys_coord[0], phys_coord[1], phys_dimensions[0], phys_dimensions[1])
        pyglet.gl.glEnable(pyglet.gl.GL_SCISSOR_TEST)
        super(ClipLayer, self).visit()
        pyglet.gl.glDisable(pyglet.gl.GL_SCISSOR_TEST)

class PopulationChoiceMenu(Menu):
    def __init__(self, game, board_layer, resource_slot_sprite, player):
        super(PopulationChoiceMenu, self).__init__()
        items = [
                 MenuItem('money', self.on_money),
                 MenuItem('material', self.on_material),
                 MenuItem('science', self.on_science)
                 ]
        
        self.menu_valign = BOTTOM
        self.menu_halign = LEFT
        
        self.game = game
        self.board_layer = board_layer
        self.resource_slot_sprite = resource_slot_sprite
        self.player = player
        
        self.create_menu(items, layout_strategy = verticalMenuLayout)
        
    @decorator
    def on_money(self):        
        return 'money'
    
    @decorator   
    def on_material(self):
        return 'material'
    
    @decorator
    def on_science(self):
        return 'science'
        
    def on_quit(self):
        pyglet.app.exit()
        
class GalaxyBoardLayer(ScrollableLayer):
    is_event_handler = True
    def __init__(self, scroller, main_screen, hud_layer, game):
        self.px_width = 6000
        self.px_height = 6000
        super(GalaxyBoardLayer, self).__init__()
        self.add(Label('BoardLayer'))
        # self.add(Sprite(pyglet.resource.image('milkyway.jpg'), scale = 0.5, position = (self.px_width / 2, self.px_height / 2)), -1)
        # self.add(Sprite(pyglet.resource.animation('planet.gif'), scale = 0.5, position = (self.px_width / 2, self.px_height / 2)))
        self.hex_width = 200
        self.hex_manager = HexManager(self.hex_width, (self.px_width / 2, self.px_height / 2))
        self.scroller = scroller
        self.scroller.set_focus(self.px_width / 2, self.px_height / 2)
        self.scroller.scale = 0.5
        self.main_screen = main_screen
        self.hud_layer = hud_layer
        self.game = game
        self.hex_layer = {}
        self.hex_sprite_slots = {}

        # wormholes
        self.wormhole_positions = [self.hex_manager.get_rel_rect_coord_from_hex_coord(0.55, 0.55),
                                  self.hex_manager.get_rel_rect_coord_from_hex_coord(1.1, 0),
                                  self.hex_manager.get_rel_rect_coord_from_hex_coord(0.55, -0.55),
                                  self.hex_manager.get_rel_rect_coord_from_hex_coord(-0.55, -0.55),
                                  self.hex_manager.get_rel_rect_coord_from_hex_coord(-1.1, 0),
                                  self.hex_manager.get_rel_rect_coord_from_hex_coord(-0.55 , 0.55)
                                  ]
        self.wormhole_rotations = [210, 270, 330, 30, 90, 150]

        # sprites
        self.sprite_slots = [self.hex_manager.get_rel_rect_coord_from_hex_coord(0.3, 0.3),
                             self.hex_manager.get_rel_rect_coord_from_hex_coord(0.6, 0.0),
                             self.hex_manager.get_rel_rect_coord_from_hex_coord(0.3, -0.3),
                             self.hex_manager.get_rel_rect_coord_from_hex_coord(-0.3, -0.3),
                             self.hex_manager.get_rel_rect_coord_from_hex_coord(-0.6, 0.0),
                             self.hex_manager.get_rel_rect_coord_from_hex_coord(-0.3, 0.3)
                             ]
        
        for coord in self.game.board.get_components().iterkeys():
            self.display_sector(coord)

    def set_hex_color(self, coord, color_name):
        if coord not in self.hex_layer:
            layer = Layer()
            rect_position = self.hex_manager.get_rect_coord_from_hex_coord(*coord)
            layer.position = rect_position
            self.hex_layer[coord] = layer
            self.hex_sprite_slots[coord] = {}
            self.add(layer)
            hex_frame = Sprite('infhexa.png', scale = 0.85)
            layer.add(hex_frame, name = 'frame')
            disc = Sprite('influence white.png', scale = 0.3)
            layer.add(disc, name = 'disc')
        color = color_convert(color_name)
        self.hex_layer[coord].get(name = 'frame').color = color
        disc = self.hex_layer[coord].get(name = 'disc')
        if color_name == 'grey':
            disc.visible = False
        else:
            disc.visible = True
            disc.color = color

    def is_hex_rotating(self, coord):
        frame = self.hex_layer[coord].get(name = 'frame')
        return frame.are_actions_running()

    def rotate_hex(self, coord, amount = 1):
        if coord in self.hex_layer:
            frame = self.hex_layer[coord].get(name = 'frame')
            if not frame.are_actions_running():
                rotate = Rotate(60 * amount, 0.2 * amount)
                frame.do(rotate)

    def display_sector(self, coord):
        sector = self.game.board.get_components()[coord]
        try:
            color_name = sector.get_components(InfluenceDisc)[0].color
        except:
            color_name = 'grey'
        self.set_hex_color(coord, color_name)
        hex_layer = self.hex_layer[coord]

        # wormholes
        for n, (pos, rot) in enumerate(zip(self.wormhole_positions, self.wormhole_rotations)):
            is_wormhole = sector.wormholes[(n - sector.rotation) % 6] == 1
            if is_wormhole:
                wormhole_sprite = Sprite('wormhole.png',
                                         position = pos,
                                         scale = 0.05
                                         )
                wormhole_sprite.rotation = rot
                hex_layer.get(name = 'frame').add(wormhole_sprite, z = 1)

        # ships
        for ship in sector.get_components(Ship):
            ship_picture = {Interceptor : 'interceptor.png',
                            Cruiser     : 'cruiser.png',
                            Dreadnought : 'dreadnought.png',
                            Starbase    : 'starbase.png'
                            }[ship.__class__]
                
            ship_coord = self.get_sprite_coord(coord)
            ship_sprite = SelectableSprite(ship,
                                            ship_picture,
                                            scale = 0.2,
                                            position = ship_coord,
                                            color = color_convert(ship.color)
                                           )
            hex_layer.add(ship_sprite, z = 1)
            
        # planets
        all_slots = {None:[],
                 'money':[],
                 'science':[],
                 'material':[]
                 }
        for slot in sector.get_components(ResourceSlot):
            all_slots[slot.resource_type].append(slot)

        for resource_type, slots in all_slots.iteritems():
            if len(slots) == 0:
                continue
            world_color = color_convert(resource_type)
            position = self.get_sprite_coord(coord)         
            planet_sprite = Sprite('planet.png',
                                    position = position,
                                    scale = 0.05,
                                    color = world_color
                                   )
            hex_layer.add(planet_sprite, z = 1)
            x, y = position
            for slot, slot_position in zip(slots, [(x - 10, y), (x + 10, y)]):
                slot_picture = 'slot_wild_adv.png' if slot.advanced else 'slot_wild.png'
                slot_sprite = SelectableSprite(slot,
                                               slot_picture,
                                               position = slot_position,
                                               color = world_color,
                                               scale = 0.2)
                hex_layer.add(slot_sprite, z = 2)
                if len(slot.get_components()) == 1:
                    population_sprite = Sprite('population white.png',
                                               position = slot_position,
                                               color = color_convert(color_name),
                                               scale = 0.22)
                    hex_layer.add(population_sprite, z = 3)
                
        # vp
        vp = sector.victory_points
        vp_picture = {1 :'reputation1.png',
                      2 :'reputation2.png',
                      3 :'reputation3.png',
                      4 :'reputation4.png'}[vp]
        vp_sprite = Sprite(vp_picture,
                           position = (17, 17),
                           scale = 0.2)
        hex_layer.add(vp_sprite, z = 1)
        
        # artifact
        if sector.artifact:
            artifact_sprite = Sprite('artifact.png',
                                     position = (27, 27),
                                     scale = 0.5
                                     )
            hex_layer.add(artifact_sprite, z = 1)
        
        # discovery
        if len(sector.get_components(DiscoveryTile)):
            discovery_tile_sprite = Sprite('discovery_tile_back.png',
                                           scale = 0.3
                                           )
            hex_layer.add(discovery_tile_sprite, name = 'discovery', z = 2)
        
        # ancients and gdc (npc)
        n_ancients = len(sector.get_components(AncientShip))
        for n in range(n_ancients):
            ancient_sprite = Sprite('ancient_ship.png',
                                    position = (-10 * n, 10 * n),
                                    scale = 0.3
                                    )
            hex_layer.add(ancient_sprite, z = 3)
        if len(sector.get_components(GalacticCenterDefenseSystem)):
            gdc_sprite = Sprite('gdc.png',
                                scale = 0.3
                                )
            hex_layer.add(gdc_sprite, z = 3)

    def get_sprite_coord(self, coord):
        options = range(len(self.sprite_slots))
        random.shuffle(options)
        for index in options:
            if index not in self.hex_sprite_slots[coord]:
                self.hex_sprite_slots[coord][index] = True
                return self.sprite_slots[index]

    def on_mouse_press(self, screen_x, screen_y, button, modifiers):
        x, y = self.scroller.pixel_from_screen(screen_x, screen_y)
        hex_u, hex_v = self.hex_manager.get_hex_from_rect_coord(x, y)
        coord = (hex_u, hex_v)
        
        if self.main_screen.current_gui_action is not None:
            if self.main_screen.current_gui_action.on_hex_mouse_click(coord, button, modifiers):
                return EVENT_HANDLED
        
        sector = self.game.board.get_components(coord, Sector)

        if modifiers & MOD_CTRL:
            self.rotate_hex(coord)
            return EVENT_HANDLED
        
        # Selectable sprite
        if coord in self.hex_layer:
            for child in self.hex_layer[coord].get_children():            
                if isinstance(child, SelectableSprite):
                    if child.get_AABB().contains(x, y):
                        if isinstance(child.obj, ResourceSlot) and button == RIGHT and len(sector.get_components(InfluenceDisc)):                        
                            # if it is a wild resource slot, then ask the player which material it is
                            if child.obj.resource_type is None:
                                player = sector.get_components(InfluenceDisc)[0].owner
                                popup = PopulationChoiceMenu(self.game, self, child, player)                                                        
                                popup.position = self.get_ancestor(ScrollingManager).pixel_to_screen(x, y)                            
                                popup_layer = self.get_ancestor(BoardScene).popup_layer                                                        
                                popup_layer.add(popup)
                            
                            elif len(child.obj.get_components()) == 1:  # remove population cube
                                cube = child.obj.get_components()[0]
                                self.game.move(child.obj, cube.owner.personal_board.population_track, resource_type = child.obj.resource_type)
                                child.remove(child.get_children()[0])
                            else:
                                player = sector.get_components(InfluenceDisc)[0].owner
                                self.game.move(player.personal_board.population_track, child.obj, resource_type = child.obj.resource_type)
                                color = color_convert(player.color)
                                population_sprite = Sprite('population white.png',
                                                           position = child.position,
                                                           color = color,
                                                           scale = 0.2
                                                           )
                                child.add(population_sprite, 1)
                            return EVENT_HANDLED
                        
                        elif isinstance(child.obj, Ship):
                            self.hud_layer.update_fleet([child.obj])
                        

        elif sector is not None:
            self.hud_layer.set_info(str(sector))
            
        return EVENT_HANDLED

    def get_hex_from_screen_coords(self, x, y):
        x, y = self.scroller.pixel_from_screen(x, y)
        return self.hex_manager.get_hex_from_rect_coord(x, y)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.main_screen.current_gui_action is not None:
            x, y = self.scroller.pixel_from_screen(x, y)
            coords = self.hex_manager.get_hex_from_rect_coord(x, y)
            self.main_screen.current_gui_action.on_hex_mouse_move(coords)
        
    def draw_hex_outline(self, coords, text = None, color = (255, 255, 255, 255), z = 2):        
        centre = self.hex_manager.get_rect_coord_from_hex_coord(*coords)
        hex_coord = []
        hex_centre = centre
        hex_r = self.hex_width / 2
        hex_vert = hex_r / math.sqrt(3)
        hex_coord.append((hex_centre[0], hex_centre[1] + 2 * hex_vert))
        hex_coord.append((hex_centre[0] + hex_r, hex_centre[1] + hex_vert))
        hex_coord.append((hex_centre[0] + hex_r, hex_centre[1] - hex_vert))
        hex_coord.append((hex_centre[0], hex_centre[1] - 2 * hex_vert))
        hex_coord.append((hex_centre[0] - hex_r, hex_centre[1] - hex_vert))
        hex_coord.append((hex_centre[0] - hex_r, hex_centre[1] + hex_vert))   
        width = 3
        line1 = Line(hex_coord[0], hex_coord[1], color, width)
        line2 = Line(hex_coord[1], hex_coord[2], color, width)
        line3 = Line(hex_coord[2], hex_coord[3], color, width)
        line4 = Line(hex_coord[3], hex_coord[4], color, width)
        line5 = Line(hex_coord[4], hex_coord[5], color, width)
        line6 = Line(hex_coord[5], hex_coord[0], color, width)
        self.add(line1, z)
        self.add(line2, z)
        self.add(line3, z)
        self.add(line4, z)
        self.add(line5, z)
        self.add(line6, z)
        result = [line1, line2, line3, line4, line5, line6]
        if text is not None:
            label = Label(text, font_name = 'Estrogen', position = hex_centre, font_size = 24,
                          anchor_x='center', anchor_y='center')
            self.add(label, z)
            result.append(label)
        return result
        
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.scroller.scale += scroll_y * 0.1
        self.scroller.scale = min(max(self.scroller.scale, 0.2), 2)
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        fx, fy = self.scroller.fx, self.scroller.fy
        xdx, ydy = self.scroller.pixel_from_screen(x + dx, y + dy)
        x, y = self.scroller.pixel_from_screen(x, y)        
        dx = xdx - x
        dy = ydy - y
        x_focus = fx - dx
        y_focus = fy - dy
        self.scroller.set_focus(x_focus, y_focus)
        
    def on_enter(self):
        super(GalaxyBoardLayer, self).on_enter()
        self.scroller = self.get_ancestor(ScrollingManager)
        
class PlayerBoardLayer(Layer):
    is_event_handler = True
    def __init__(self, player):        
        super(PlayerBoardLayer, self).__init__()
        self.player = player
        self.color = color_convert(self.player.color)
        self.add(Label('PlayerBoardLayer'))
        width, height = director.get_window_size()
        position = (width / 2, height / 2)
        player_board_sprite = BackgroundSprite(str(player.faction.board),
                                     position = position                              
                                     )
        self.add(player_board_sprite)
        self.scale = min(1.0 * width / player_board_sprite.image.width, 1.0 * height / player_board_sprite.image.height)
        # defining the rectangular zone
        self.rect_player_board = player_board_sprite.get_AABB()
        # width, heigth = self.rect_player_board.size ----> bug ?
        width = self.rect_player_board.width
        height = self.rect_player_board.height
        x, y = self.rect_player_board.bottomleft        
        
        self.rect_influence = Rect(x + 0.106 * width,
                                   y + 0.076 * height,
                                   width * 0.725,
                                   height * 0.07)
        self.rect_action_board = Rect(x + 0.49 * width,
                                      y + 0.175 * height,
                                      width * 0.355,
                                      height * 0.125)
        self.rect_population_material = Rect(x + 0.105 * width,
                                             y + 0.17 * height,
                                             width * 0.38,
                                             height * 0.04)        
        self.rect_population_science = Rect(x + 0.105 * width,
                                            y + 0.215 * height,
                                            width * 0.38,
                                            height * 0.04)        
        self.rect_population_money = Rect(x + 0.105 * width,
                                          y + 0.262 * height,
                                          width * 0.38,
                                          height * 0.04)
        self.refresh_display()
        
    def refresh_display(self):
        # erase all sprites but the background
        for child in self.get_children():
            if isinstance(child, Sprite) and not isinstance(child, BackgroundSprite):
                child.kill()
        # influence track
        n_influence = len(self.player.personal_board.influence_track.get_components())
        for n in range(n_influence):
            position = self.get_influence_coord(n)
            influence_sprite = Sprite('influence white.png',
                                      position = position,
                                      color = self.color,
                                      scale = 0.9)
            self.add(influence_sprite, 2)
        # action board
        for action_index in range(6):
            action = ActionBoard.action_names[action_index];
            n_influence = len(self.player.personal_board.action_board.get_components(action))
            for n in range(n_influence):
                sprite = Sprite('influence white.png',
                                color = self.color,
                                position = self.get_action_coord(action_index, n),
                                scale = 0.9)
                self.add(sprite, z = n + 1)
            
        # population track(s)
        for track in self.player.personal_board.population_track.get_zones().itervalues():
            n_pop = len(track.get_components())
            for n in range(n_pop):
                position = self.get_population_coord(n, track.resource_type)
                population_sprite = Sprite('population white.png',
                                           position = position,
                                           color = self.color,
                                           scale = 0.45)
                self.add(population_sprite, 2)
            
    def on_enter(self):
        self.refresh_display()
        return Layer.on_enter(self)
        
    def get_influence_coord(self, n):
        """
        Get the coordinates to place the influence sprites on the influence track.
        n = 0 is the influence to the extreme left and n = 12 is the one the
        extreme right.
        """
        rect = self.rect_influence
        x = rect.left + (n + 0.5) / 13 * rect.width
        y = rect.bottom + 0.5 * rect.height
        return (x, y)
    
    def get_action_coord(self, action_index, n):
        """
        Get the coordinates to place the influence disc sprite on the action board.
        """
        width = self.rect_action_board.width * 0.95
        offset_x = (self.rect_action_board.width - width) * 0.7
        x = int(offset_x + (action_index + 0.5) * width / 6.0)
        y = self.rect_action_board.height * 0.35
        return (self.rect_action_board.x + x + 6*n, self.rect_action_board.y + y + 7*n)
    
    def get_population_coord(self, n, resource_type):
        """
        Get the coordinates to place the population sprites on the population track.
        n = 0 is the population to the extreme left and n = 12 is the one the
        extreme right.
        resource_type is either 'money', 'material' or 'science'
        """
        rect = {'money':    self.rect_population_money,
                'science':  self.rect_population_science,
                'material': self.rect_population_material
                }[resource_type]
        x = rect.left + (n + 0.5) / 12 * rect.width
        y = rect.bottom + 0.5 * rect.height
        return (x, y)
        
    def draw_grid(self, rect, nh, nv):
        # horizontal lines
        for n in range(nh):
            x1 = rect.left
            x2 = rect.right
            y = rect.bottom + 1.0 * n / nh * rect.height
            a = (x1, y)
            b = (x2, y)
            self.add(Line(a, b, (255, 255, 255, 255)), 2)
        # vertical lines
        for n in range(nv):
            x = rect.left + 1.0 * n / nv * rect.width
            y1 = rect.top
            y2 = rect.bottom
            a = (x, y1)
            b = (x, y2)
            self.add(Line(a, b, (255, 255, 255, 255)), 2)
        
    def draw_rect(self, rect):   
        for line in ((rect.topleft, rect.topright),
                     (rect.topright, rect.bottomright),
                     (rect.bottomright, rect.bottomleft),
                     (rect.bottomleft, rect.topleft)):
            self.add(Line(line[0], line[1], (255, 255, 255, 255)), 2)
            
    def on_mouse_press (self, x, y, button, modifiers):
        x, y = director.get_virtual_coordinates(x, y)
        print self.rect_player_board.contains(x, y)
        
class ResearchBoardLayer(Layer):
    is_event_handler = True
    def __init__(self):
        super(ResearchBoardLayer, self).__init__()
        width, height = director.get_window_size()
        position = (width / 2, height / 2)
        research_board_sprite = BackgroundSprite('research_board.png',
                                                 position = position,
                                                 scale = 1.5)
        self.add(research_board_sprite)
        
class Hide(IntervalAction):
    def __init__(self, duration):
        self.duration = duration
        
    def update(self, t):
        if t >= 1.0:
            self.target.visible = False
    

class HudLayer(Layer):
    is_event_handler = True
    def __init__(self, game, main_screen):
        super(HudLayer, self).__init__()
        self.game = game
        self.main_screen = main_screen
        self.current_player = None
        
        # hud scale
        self.scale_hud = min(director.get_window_size()[0] / 1920.0, director.get_window_size()[1] / 1080.0)

        self.action_board = ActionBoardLayer(position = (director.get_window_size()[0], 0), scale = 0.3 * self.scale_hud)
        self.add(self.action_board)

        self.influence_layer = HudInfluenceTrackLayer(scale = 1.2 * self.scale_hud)
        self.add(self.influence_layer)
        self.influence_disc = Sprite('influence white.png', scale = 0.96 * self.scale_hud)
        self.influence_disc.visible = False
        self.add(self.influence_disc)
        self.influence_disc_component = None
        
        self.turn_button = Sprite('turn_button.png',
                                  anchor = (0, 0),
                                  scale = self.scale_hud
                                  )
        
        self.add(self.turn_button)
                
        # message        
        self.base_color = (0, 205, 0, 200)
        self.info = Label('',
                          (0, director.get_window_size()[1] - 50),
                          font_name = 'Estrogen',
                          font_size = 15,
                          color = self.base_color,
                          width = 1000,
                          multiline = True)
        self.add(self.info)
        
        self.schedule_interval(self.update_time, .1)
        
        # fleet manager
        self.fleet_manager_frame = AnchorSprite('fleet_manager.png', scale = 0.5 * self.scale_hud, anchor = (1.0, 1.0))
        self.fleet_manager_frame.position = director.get_window_size()
        self.add(self.fleet_manager_frame)


        self.sub_layer = Layer()
        self.fleet_manager_frame.add(self.sub_layer)
        
        # kick off first turn
        self.main_screen.set_state('action phase')
        
    def do_resize(self, virtual_offset_x, virtual_offset_y):
        rhs, top = director.get_window_size()
        self.fleet_manager_frame.position = (rhs + virtual_offset_x, top + virtual_offset_y)
        self.action_board.position = (rhs + virtual_offset_x, -virtual_offset_y)
        self.turn_button.position = (-virtual_offset_x, -virtual_offset_y)
        self.influence_layer.position = (rhs + virtual_offset_x, self.action_board.get_height() - virtual_offset_y)
        
    def update_fleet(self, ships):
        # refresh the frame
        for child in self.sub_layer.get_children():
            child.kill()
        
        # get all the owners
        owners = set([ship.owner for ship in ships])
        for owner in owners:        
            ship_names = set([ship.name for ship in ships if ship.owner is owner])
            for n, ship_name in enumerate(ship_names):               
            
                scale = 0.7
                fleet_manager_size = (919, 1252)
                y_pos = -250 - 300 * n
                ship_sprite = Sprite(ship_name + '.png',
                                     (-fleet_manager_size[0] + 200, y_pos),
                                     scale = scale,
                                     color = color_convert(owner.color))   
                
                self.sub_layer.add(ship_sprite)
                """
                ship_parts = owner.personal_board.blueprints.get_ship_parts(ship_name)
                for m, ship_part in enumerate(ship_parts):
                    ship_part_sprite = Sprite(ship_part.name + '.png', (-fleet_manager_size[0] + 500 + 100 * m, y_pos), scale = 0.8)
                    self.fleet_manager_frame.add(ship_part_sprite)
                """
                
                ship_stats = owner.personal_board.blueprints.get_stats(ship_name)
                non_weapon_stats = ['initiative', 'movement', 'hull', 'computer', 'shield']
                for m, stat_name in enumerate(non_weapon_stats):
                    label_stat = Label('',
                                      (-fleet_manager_size[0] + 400, y_pos + 60 - 40 * m),
                                      font_name = 'Estrogen',
                                      font_size = 30,
                                      color = self.base_color,
                                      width = 1000,
                                      multiline = True)
                    self.sub_layer.add(label_stat)
                    label_stat.do(InfoAction(stat_name + ' : ' + str(ship_stats[stat_name]), '', 0.4))

    def update_time(self, dt):
        new_color = [0, random.randint(230, 255), 0, 255]       
        self.info.element.color = new_color
        if self.current_player is not self.game.current_player:
            self.refresh_current_player()
        
    def set_info(self, text):
        self.info.do(InfoAction(text, '_', 0.4))
        
    def get_influence_disc_drop_target(self):
        if self.main_screen.player_action is None:
            return 'actionBoard'
        else:
            return self.main_screen.current_gui_action.get_influence_disc_drop_target()

    def on_mouse_press(self, x, y, button, modifiers): 
        x, y = director.get_virtual_coordinates(x, y)
        if self.turn_button.contains(x, y):
            self.end_turn()
            return EVENT_HANDLED
        elif self.influence_layer.click_current_disc(x, y, self.current_player):
            target = self.get_influence_disc_drop_target()
            if target is not None:
                self.start_drag_disc(x, y, self.current_player.personal_board.influence_track)
                self.influence_layer.refresh(self.current_player, False)
                return EVENT_HANDLED

    def start_drag_disc(self, x, y, zone):
        self.influence_disc.color = color_convert(self.current_player.color)
        self.influence_disc.visible = True
        self.influence_disc.position = (x, y)
        self.influence_disc_component = zone.take()
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.influence_disc_component is not None:
            self.influence_disc.position = director.get_virtual_coordinates(x, y)
            return EVENT_HANDLED
    
    def on_mouse_release(self, x, y, buttons, modifiers):
        if self.influence_disc_component is not None:
            target = self.get_influence_disc_drop_target()
            if target == 'actionBoard':
                x, y = director.get_virtual_coordinates(x, y)
                action = self.action_board.get_action_from_coords(x, y)
                if action is not None:
                    self.set_info('Select Action: ' + action)
                    player_action = self.current_player.faction.actions[ActionBoard.action_names.index(action)]
                    self.main_screen.set_player_action(player_action)
                    self.current_player.personal_board.action_board.add(action, self.influence_disc_component)
                    self.influence_disc_component = None
                    self.influence_disc.visible = False
                    self.refresh_influence_track()
                    self.action_board.refresh(self.current_player)
                    return EVENT_HANDLED
            elif isinstance(target, tuple):
                # Target is a hex coordinate
                disc_coord = self.main_screen.board_scene.board_layer.get_hex_from_screen_coords(x, y)
                if disc_coord == target:
                    sector = self.game.board.get_components(target, Sector)
                    if len(sector.get_components(InfluenceDisc)) == 0:
                        sector.add(self.influence_disc_component)
                        self.influence_disc_component = None
                        self.influence_disc.visible = False
                        self.main_screen.board_scene.board_layer.set_hex_color(target, self.game.current_player.color)
                        self.refresh_influence_track()
                        return EVENT_HANDLED
            self.return_influence_disc()

    def return_influence_disc(self):
        n_influence = len(self.current_player.personal_board.influence_track.get_components())
        position = self.influence_layer.get_global_disc_position(n_influence)
        self.current_player.personal_board.influence_track.add(self.influence_disc_component)
        self.influence_disc.do(MoveTo(position, duration = 0.5) + Hide(duration = 0.01))
        
    def draw(self):
        if self.influence_disc_component is not None and not self.influence_disc.visible:
            self.influence_disc_component = None
            self.refresh_influence_track()
        super(HudLayer, self).draw()

    def end_turn(self):
        self.main_screen.next_player_action_phase()
        self.refresh_current_player()
        
    def refresh_current_player(self):
        self.current_player = self.game.current_player
        self.turn_button.color = color_convert(self.current_player.color)
        self.action_board.refresh(self.current_player)
        self.refresh_influence_track()
            
    def refresh_influence_track(self):
        self.influence_layer.refresh(self.current_player)

class ActionBoardLayer(Layer):
    def __init__(self, position = (0, 0), scale = 1.0):
        super(ActionBoardLayer, self).__init__()
        self.position = position
        self.action_board_blank = AnchorSprite('boards/action_board.png',
                                               anchor = (1.0, 0),
                                               scale = scale)
        self.add(self.action_board_blank, -1)
        self.action_sprites = {}
        self.action_position = [0.2, 1.12, 2.05, 3, 3.95, 4.9]
        self.selection_sprite = AnchorSprite('action_selection_halo.png',
                                             scale = scale,
                                             anchor = (0.5, 0),
                                             position = position)
        

    def get_height(self):
        return self.action_board_blank.height

    def refresh(self, current_player):
        for action in self.action_sprites:
            self.action_sprites[action].visible = False
        for action in current_player.faction.actions:
            if action not in self.action_sprites:
                image = 'image/boards/action_' + action + '.png'
                sprite = AnchorSprite(image, anchor = (1.0, 0), scale = self.action_board_blank.scale)
                self.add(sprite)
                self.action_sprites[action] = sprite
            self.action_sprites[action].visible = True
        for child in self.get_children():
            if not isinstance(child, AnchorSprite):
                child.kill()
        for action_index in range(6):
            action = ActionBoard.action_names[action_index]
            n_influence = len(current_player.personal_board.action_board.get_components(action))
            for n in range(n_influence):
                sprite = Sprite('influence white.png',
                                color = color_convert(current_player.color),
                                position = self.disc_position(action_index, n),
                                scale = 0.32)
                self.add(sprite, z = n + 1)

    def disc_position(self, action_index, n):
        width = self.action_board_blank.width * 0.95
        offset_x = (self.action_board_blank.width - width) / 2
        x = int(offset_x + (action_index + 0.5) * width / 6 - self.action_board_blank.width)
        y = self.action_board_blank.height * 0.45
        return (x + 1.6*n, y + 2.9*n)

    def get_action_from_coords(self, x, y):
        rect = self.action_board_blank.get_AABB()
        rect.right = self.position[0]
        if rect.contains(x, y):
            dx = rect.width / 6.0
            n = int((x - rect.left) / dx)
            return ActionBoard.action_names[n]
        else:
            return None

class HudInfluenceTrackLayer(ClipLayer):
    def __init__(self, scale = 1.0):
        super(HudInfluenceTrackLayer, self).__init__(Rect(int(scale * -240), 0, int(scale * 240), int(scale * 104)))
        track = pyglet.resource.image('boards/influence_track.png')
        self.size = (track.width, track.height)
        self.influence_track_sprite = AnchorSprite(track,
                                                   anchor = (1.0, 0),
                                                   scale = scale)
        self.add(self.influence_track_sprite)
        self.influence_disc_sprite = []
        for count in range(13):
            self.influence_disc_sprite.append(AnchorSprite('influence white.png',
                                                            anchor = (0.5, 0.5),
                                                            position = self.get_disc_position(count),
                                                            scale = 0.8))
            self.influence_track_sprite.add(self.influence_disc_sprite[count])

    def get_disc_position(self, n):
        width = self.size[0] * 0.9
        offset_x = (self.size[0] - width) / 2
        return (offset_x + width * n / 12 - self.size[0], self.size[1] * 0.55)

    def get_global_disc_position(self, n):
        position = self.get_disc_position(n)
        adjust = adjust_for_parents(self.influence_track_sprite)
        x = position[0] * adjust[2] + adjust[0]
        y = position[1] * adjust[2] + adjust[1]
        return (int(x), int(y))

    def refresh(self, current_player, move = True):
        n_influence = len(current_player.personal_board.influence_track.get_components())
        for count in range(13):
            self.influence_disc_sprite[count].color = color_convert(current_player.color)
            self.influence_disc_sprite[count].visible = (count < n_influence)
        if move:
            left = int(self.get_disc_position(24.8 - n_influence)[0]*self.influence_track_sprite.scale)
            self.influence_track_sprite.do(MoveTo((left, 0), duration = 0.5))

    def click_current_disc(self, x, y, current_player):
        n_influence = len(current_player.personal_board.influence_track.get_components())
        return n_influence > 0 and self.influence_disc_sprite[n_influence - 1].contains(x, y)


class PopUpLayer(Layer):
    """
    Layer that is meant to contain pop up menus. When a pop up menu appears, all keypad/mouse events are intercepted
    and won't be propagated to the lower layers.
    """
    is_event_handler = True
    def __init__(self, game):
        super(PopUpLayer, self).__init__()
        self.game = game
        self.is_active = False  # will be set to True if a pop up appears. This variable is used to test if the events are to be propagated through the lower layers
        
    def add(self, child, z = 0, name = None):
        super(PopUpLayer, self).add(child, z, name)
        self.is_active = True
        
    def remove(self, obj):
        super(PopUpLayer, self).remove(obj)
        if not len(self.get_children()):
            self.is_active = False
        
    def on_mouse_press(self, *args):
        if self.is_active:
            return EVENT_HANDLED
    
    def on_mouse_motion(self, *args):
        if self.is_active:
            return EVENT_HANDLED
        
    def on_mouse_scroll(self, *args):
        if self.is_active:
            return EVENT_HANDLED
        
    def on_mouse_drag(self, *args):
        if self.is_active:
            return EVENT_HANDLED            
  
class BoardScene(Scene):
    def __init__(self, game, main_screen):
        super(BoardScene, self).__init__()
        self.game = game
        self.add(ColorLayer(0, 0, 0, 255), 0)
        scroller = ScrollingManager()
        self.hud_layer = HudLayer(game, main_screen)
        self.popup_layer = PopUpLayer(game)
        self.board_layer = GalaxyBoardLayer(scroller, main_screen, self.hud_layer, game)
        scroller.add(self.board_layer)
        self.add(scroller, 1)
        self.add(self.hud_layer, 4)
        self.add(self.popup_layer, 5)
        director.push_handlers(self)

    def on_resize(self, new_width, new_height):
        virtual_offset_x, virtual_offset_y = 0, 0
        virtual_width, virtual_height = director.get_window_size()
        if director._offset_x > 0:
            virtual_offset_x = 1.0 * virtual_width * director._offset_x / director._usable_width 
        if director._offset_y > 0:
            virtual_offset_y = 1.0 * virtual_height * director._offset_y / director._usable_height 
        virtual_max_x = virtual_width + virtual_offset_x
        virtual_max_y = virtual_height + virtual_offset_y
        # Adjust projection matrix to expose entire screen
        glViewport(0, 0, new_width, new_height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-virtual_offset_x, virtual_max_x, -virtual_offset_y, virtual_max_y, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Adjust HUD elements
        self.hud_layer.do_resize(virtual_offset_x, virtual_offset_y)

    def on_enter(self):
        super(BoardScene, self).on_enter()
        self.on_resize(director._usable_width + 2 * director._offset_x, director._usable_height + 2 * director._offset_y)

    def highlight_hexes(self, hexes):
        sprites = []
        for coord in hexes:
            text = None
            if self.game.board.get_components(coord = coord) is None:
                ring = self.game.get_coord_ring(coord)
                text = 'I' * ring
            lines = self.board_layer.draw_hex_outline(coord, color = (180, 180, 180, 255), text = text)
            sprites.extend(lines)
        return sprites
            

class PlayerBoardScene(Scene):
    def __init__(self, player):
        super(PlayerBoardScene, self).__init__()
        self.add(ColorLayer(200, 200, 200, 255), 0)
        self.add(PlayerBoardLayer(player), 1)
        self.player = player
        
class ResearchBoardScene(Scene):
    def __init__(self):
        super(ResearchBoardScene, self).__init__()
        self.add(ColorLayer(100, 100, 100, 255), 0)
        self.add(ResearchBoardLayer(), 1)
        
class MainScreen(Layer):
    is_event_handler = True    
    def __init__(self, game):
        super(MainScreen, self).__init__()
        self.game = game
        self.scenes = {}
        self.board_scene = BoardScene(game, self)
        self.add_scene(self.board_scene, B)
        for n, player in enumerate(game.players):
            scene = PlayerBoardScene(player)
            self.add_scene(scene, _1 + n)
        self.research_board_scene = ResearchBoardScene()
        self.add_scene(self.research_board_scene, R)
        director.replace(ZoomTransition(self.board_scene, 1.0))
        self.schedule_interval(self.update_time, .1)
        self.initialise_gui_actions()

    def on_key_press(self, key, modifiers):
        if key == P:
            self.show_current_player_board()
        elif key in self.scenes:
            self.transition(self.scenes[key])

    def transition(self, scene):
        if scene != director.scene:
            director.replace(FadeUpTransition(scene, duration = 0.3))

    def show_current_player_board(self):
        current_player = self.game.current_player
        scene = [scene for scene in self.scenes.itervalues()
                 if isinstance(scene, PlayerBoardScene)
                 and scene.player == current_player
                 ][0]
        self.transition(scene)

    def add_scene(self, scene, key):
        """
        Add a new scene to the control layer that may be displayed by pressing
        the corresponding key button.
        the key must be an integer corresponding to a pyglet key from
        pyglet.window.key.
        This method also add the control layer to the scene as a child.
        """
        self.scenes[key] = scene
        scene.add(self)

    def initialise_gui_actions(self):
        self.gui_action = {}
        self.gui_action[UIAction.show_hex_map] = ShowSceneGuiAction(self.game, self, self.scenes[B])
        self.gui_action[UIAction.select_unexplored_hex] = SelectUnexploredHexGuiAction(self.game, self)
        self.gui_action[UIAction.select_from_hex] = SelectFromHexGuiAction(self.game, self)
        self.gui_action[UIAction.rotate_reject_hex] = RotateRejectGuiAction(self.game, self)

        self.gui_action[UIAction.show_research_board] = ShowSceneGuiAction(self.game, self, self.scenes[R])
        self.gui_action[UIAction.show_blueprints] = ShowCurrentPlayerBoardGuiAction(self.game, self)

    def set_state(self, state):
        if state == 'action phase':
            self.action_ui_count = 0
            self.action_state = {}
            self.player_action = None
            self.current_gui_action = None

    def next_player_action_phase(self):
        if self.player_action is None:
            # TODO if they've selected an action but they haven't used it yet, then they've also passed (and return the disc)
            print 'player has passed'
            # TODO see if they're now 1st player or if the action phase is done
            # TODO these checks should be done in the game code - pass parameter to end_turn indicating if they're done anything?
        self.game.end_turn()
        self.action_ui_count = 0
        self.action_state = {}
        self.player_action = None
        self.current_gui_action = None
        
    def set_player_action(self, player_action):
        self.player_action = actions[player_action]
        self.advance_player_action_count()
    
    def advance_player_action_count(self):
        if self.current_gui_action is not None:
            self.current_gui_action.on_end()
        self.action_ui_count += 1
        ui_action = self.player_action.next(self.action_ui_count, self.action_state, self.game)
        if ui_action is None:
            self.current_gui_action = None
        else:
            self.current_gui_action = self.gui_action[ui_action]
            self.current_gui_action.on_start()

    def update_time(self, dt):
        if self.current_gui_action is not None:
            if self.current_gui_action.is_finished():
                self.advance_player_action_count()


class InfoAction(IntervalAction):
    """Action that can be applied to any Label to make a dynamic text display
    """
    def init(self, word, post_text, duration):
        self.duration = duration  # : Duration in seconds
        self.word = word
        self.word_size = len(word)
        self.post_text = post_text
        
    def start(self):
        self.current_text = ''    
        
    def update(self, t):
        current_text_size = int(t * self.word_size)
        self.current_text = self.word[0:current_text_size]
        self.current_text += self.post_text
        self.target.element.text = self.current_text
