'''
Created on 4 janv. 2012

@author: jglouis
'''
from cocos.scene import Scene
from cocos.layer.base_layers import Layer
from cocos.text import Label
from cocos.director import director
from cocos.scenes.transitions import FadeUpTransition, ZoomTransition
from cocos.layer.util_layers import ColorLayer
from cocos.draw import Line
import math
from cocos.layer.scrolling import ScrollableLayer, ScrollingManager
import pyglet
from cocos.sprite import Sprite
from hexmanager import HexManager
from cocos.actions.base_actions import IntervalAction
import random
from engine.zone import Sector, ResourceSlot, ActionBoard
from engine.component import InfluenceDisc, Ship, Interceptor, Cruiser, Dreadnought, Starbase, \
    AncientShip, GalacticCenterDefenseSystem, DiscoveryTile, PopulationCube
from pyglet.window.mouse import RIGHT
from pyglet.event import EVENT_HANDLED
from cocos.rect import Rect
from pyglet.window.key import B, R, _1, P, MOD_CTRL
from cocos.batch import BatchNode
from cocos.actions.interval_actions import Rotate, MoveTo, FadeOut
from cocos.menu import Menu, MenuItem, zoom_in, zoom_out, shake, ColorMenuItem, fixedPositionMenuLayout, LEFT, TOP, \
    BOTTOM, verticalMenuLayout
from pyglet.gl.gl import glViewport, glMatrixMode, glLoadIdentity, GL_PROJECTION, \
    GL_MODELVIEW, glOrtho

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
        
class BoardLayer(ScrollableLayer):
    is_event_handler = True
    def __init__(self, scroller, hud_layer, game):
        self.px_width = 6000
        self.px_height = 6000
        super(BoardLayer, self).__init__()
        self.add(Label('BoardLayer'))
        # self.add(Sprite(pyglet.resource.image('milkyway.jpg'), scale = 0.5, position = (self.px_width / 2, self.px_height / 2)), -1)
        # self.add(Sprite(pyglet.resource.animation('planet.gif'), scale = 0.5, position = (self.px_width / 2, self.px_height / 2)))
        self.hex_width = 200
        self.hex_manager = HexManager(self.hex_width, (self.px_width / 2, self.px_height / 2))
        self.scroller = scroller
        self.scroller.set_focus(self.px_width / 2, self.px_height / 2)
        self.scroller.scale = 0.5
        self.hud_layer = hud_layer
        self.game = game
        self.hex_color_sprites = {}
        self.hex_color_discs = {}

        self.batch1 = BatchNode()
        self.batch2 = BatchNode()
        self.batch3 = BatchNode()
        self.add(self.batch1, 1)
        self.add(self.batch2, 2)
        self.add(self.batch3, 3)
        
        for coord in self.game.board.get_components().iterkeys():
            self.display_sector(coord)
    
    def set_hex_color(self, coord, color_name):
        color = color_convert(color_name)
        if coord in self.hex_color_sprites:
            self.hex_color_sprites[coord].color = color
            if color_name == 'grey':
                self.hex_color_discs[coord].visible = False
            else:
                self.hex_color_discs[coord].visible = True
                self.hex_color_discs[coord].color = color
        else:
            u, v = coord
            rect_position = self.hex_manager.get_rect_coord_from_hex_coord(u, v)
            hexa = Sprite('infhexa.png',
                scale = 0.85,
                position = rect_position,
                color = color)
            
            batch = BatchNode()
            batch.anchor = rect_position
            self.add(batch, name = str(coord))
            batch.add(hexa)
            self.hex_color_sprites[coord] = hexa
            disc = Sprite('influence white.png',
                          scale = 0.3,
                          position = rect_position,
                          color = color)
            batch.add(disc)
            if color_name == 'grey':
                disc.visible = False
            self.hex_color_discs[coord] = disc
            
    def rotate_hex(self, coord):
        rotate = Rotate(60, 0.2)
        try:
            batch = self.get(name = str(coord))
            if not batch.are_actions_running():
                batch.do(rotate)
                self.game.rotate_hex(coord)
        except:
            pass
        
    def display_sector(self, coord):                   
        u, v = coord
        sector = self.game.board.get_components()[coord]
        rect_position = self.hex_manager.get_rect_coord_from_hex_coord(u, v)
        
        # hex_color
        try:
            color = sector.get_components(InfluenceDisc)[0].color
        except:
            color = 'grey'
        self.set_hex_color(coord, color)

        # wormholes
        wormhole_positions = [(0.5, 0.5),
                              (1.0, 0),
                              (0.5, -0.5),
                              (-0.5, -0.5),
                              (-1.0, 0),
                              (-0.5 , 0.5)
                              ]
        wormhole_rotations = [210, 270, 330, 30, 90, 150]
        
        for n, (pos, rot) in enumerate(zip(wormhole_positions, wormhole_rotations)):
            is_wormhole = sector.wormholes[(n - sector.rotation) % 6]
            if is_wormhole:
                abs_rect_pos = self.hex_manager.get_rect_coord_from_hex_coord(u + pos[0], v + pos[1])
                wormhole_sprite = Sprite('wormhole.png',
                                         position = abs_rect_pos,
                                         scale = 0.05
                                         )
                wormhole_sprite.image_anchor_y = 0
                wormhole_sprite.rotation = rot
                
                self.get(str(coord)).add(wormhole_sprite)
               
        # ships
        for ship in sector.get_components(Ship):

                
            ship_picture = {Interceptor : 'interceptor.png',
                            Cruiser     : 'cruiser.png',
                            Dreadnought : 'dreadnought.png',
                            Starbase    : 'starbase.png'
                            }[ship.__class__]
                
            ship_coord = self.hex_manager.get_sprite_coord(u, v)
            ship_sprite = SelectableSprite(ship,
                                           ship_picture,
                                           scale = 0.2,
                                           position = ship_coord,
                                           color = color_convert(ship.color)
                                           )
            self.batch1.add(ship_sprite)
            
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
            color = color_convert(resource_type)
            position = self.hex_manager.get_sprite_coord(u, v)         
            planet_sprite = Sprite('planet.png',
                                   position = position,
                                   scale = 0.05,
                                   color = color
                                   )
            self.batch1.add(planet_sprite)
            x, y = position
            for slot, position in zip(slots, [(x - 10, y), (x + 10, y)]):
                slot_picture = 'slot_wild_adv.png' if slot.advanced else 'slot_wild.png'
                slot_sprite = SelectableSprite(slot,
                                               slot_picture,
                                               position = position,
                                               color = color,
                                               scale = 0.2)
                self.batch2.add(slot_sprite)
                if len(slot.get_components()) == 1:
                    population_sprite = Sprite('population white.png',
                                               position = position,
                                               color = color_convert(slot.get_components()[0].color),
                                               scale = 0.2
                                               )
                    slot_sprite.add(population_sprite)
                
        # vp
        vp = sector.victory_points
        vp_picture = {1 :'reputation1.png',
                      2 :'reputation2.png',
                      3 :'reputation3.png',
                      4 :'reputation4.png'}[vp]
        vp_sprite = Sprite(vp_picture,
                           position = rect_position,
                           scale = 0.2)
        vp_sprite.x += 17
        vp_sprite.y += 17
        self.batch1.add(vp_sprite)
        
        # artifact
        if sector.artifact:
            artifact_sprite = Sprite('artifact.png',
                                     position = rect_position,
                                     scale = 0.5
                                     )
            artifact_sprite.x += 27
            artifact_sprite.y += 27
            self.batch1.add(artifact_sprite)
        
        # discovery
        if len(sector.get_components(DiscoveryTile)):
            discovery_tile_sprite = Sprite('discovery_tile_back.png',
                                           position = rect_position,
                                           scale = 0.3
                                           )
            self.batch2.add(discovery_tile_sprite)
        
        # ancients and gdc (npc)
        n_ancients = len(sector.get_components(AncientShip))
        for n in range(n_ancients):
            ancient_sprite = Sprite('ancient_ship.png',
                                    position = rect_position,
                                    scale = 0.3
                                    )
            ancient_sprite.x -= 20.0 * (n - (1.0 * n / n_ancients))
            ancient_sprite.y += 20.0 * (n - (1.0 * n / n_ancients))
            self.batch3.add(ancient_sprite)
        if len(sector.get_components(GalacticCenterDefenseSystem)):
            gdc_sprite = Sprite('gdc.png',
                                position = rect_position,
                                scale = 0.3
                                )
            self.batch3.add(gdc_sprite)

    def on_mouse_press(self, screen_x, screen_y, button, modifiers):               
        x, y = self.scroller.pixel_from_screen(screen_x, screen_y)
        hex_u, hex_v = self.hex_manager.get_hex_from_rect_coord(x, y)
        coord = (hex_u, hex_v)
        
        sector = self.game.board.get_components(coord, Sector)

        if modifiers & MOD_CTRL:
            self.rotate_hex(coord)
            return EVENT_HANDLED
        
        # Selectable sprite
        for child in self.batch1.get_children() + self.batch2.get_children() + self.batch3.get_children():            
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
                        

        # explore the sector if right click and sector empty
        # influence the sector if right click and not empty
        if button == RIGHT:   
            if sector is None:    
                sector_tile = self.game.draw_hex(coord)
                if sector_tile is not None:
                    self.game.place_hex(sector_tile, coord)
                    self.hud_layer.set_info('New Sector discovered: ' + sector_tile.name)
                    self.display_sector(coord)
                else:
                    self.hud_layer.set_info('No New Sector to explore -Aborting')
            elif len(sector.get_components(InfluenceDisc)) == 0:
                self.game.move(self.game.current_player.personal_board.influence_track, sector)
                self.set_hex_color(coord, self.game.current_player.color)
                self.hud_layer.set_info('Influence on sector ' + sector.name)
                self.hud_layer.refresh_influence_track()
            else:
                player = sector.get_components(InfluenceDisc)[0].owner
                self.game.move(sector, player.personal_board.influence_track, component_type = InfluenceDisc)
                self.set_hex_color(coord, 'grey')
                self.hud_layer.set_info('Influence removed from Sector')
                self.hud_layer.refresh_influence_track()
        elif sector is not None:
            self.hud_layer.set_info(str(sector))
        else:
            self.hud_layer.set_info('Unknown Sector')
            
        return EVENT_HANDLED
                
    def on_mouse_motion(self, x, y, dx, dy):    
        x, y = self.scroller.pixel_from_screen(x, y)
        hex_u, hex_v = self.hex_manager.get_hex_from_rect_coord(x, y)
        hex_x, hex_y = self.hex_manager.get_rect_coord_from_hex_coord(hex_u, hex_v)
        for child in self.get_children():
            if isinstance(child, Line):
                child.kill()
        self.add_hex((hex_x, hex_y), self.hex_width / 2)
        
    def add_hex(self, centre, r):        
        hex_coord = []
        hex_centre = centre
        hex_r = r
        hex_vert = hex_r / math.sqrt(3)
        hex_coord.append((hex_centre[0], hex_centre[1] + 2 * hex_vert))
        hex_coord.append((hex_centre[0] + hex_r, hex_centre[1] + hex_vert))
        hex_coord.append((hex_centre[0] + hex_r, hex_centre[1] - hex_vert))
        hex_coord.append((hex_centre[0], hex_centre[1] - 2 * hex_vert))
        hex_coord.append((hex_centre[0] - hex_r, hex_centre[1] - hex_vert))
        hex_coord.append((hex_centre[0] - hex_r, hex_centre[1] + hex_vert))       
        w = 3        
        line1 = Line(hex_coord[0], hex_coord[1], (255, 255, 255, 255) , w)
        line2 = Line(hex_coord[1], hex_coord[2], (255, 255, 255, 255) , w)
        line3 = Line(hex_coord[2], hex_coord[3], (255, 255, 255, 255) , w)
        line4 = Line(hex_coord[3], hex_coord[4], (255, 255, 255, 255) , w)
        line5 = Line(hex_coord[4], hex_coord[5], (255, 255, 255, 255) , w)
        line6 = Line(hex_coord[5], hex_coord[0], (255, 255, 255, 255) , w)
        self.add(line1, 2)
        self.add(line2, 2)
        self.add(line3, 2)
        self.add(line4, 2)
        self.add(line5, 2)
        self.add(line6, 2)   
        
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
        super(BoardLayer, self).on_enter()
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
        
class ControlLayer(Layer):
    """
    The control layer is unique. It handles the switching
    between the different scenes.
    """
    is_event_handler = True    
    def __init__(self, game):
        super(ControlLayer, self).__init__()
        self.game = game
        self.scenes = {}
        
    def on_key_press(self, key, modifiers):
        try:
            if key == P:
                current_player = self.game.current_player
                scene = [scene for scene in self.scenes.itervalues()
                         if isinstance(scene, PlayerBoardScene)
                         and scene.player == current_player
                         ][0]
                director.replace(FadeUpTransition(scene, duration = 0.3))
            elif key in self.scenes:
                director.replace(FadeUpTransition(self.scenes[key], duration = 0.3))
        except:
            pass
            
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

class Hide(IntervalAction):
    def __init__(self, duration):
        self.duration = duration
        
    def update(self, t):
        if t >= 1.0:
            self.target.visible = False
    

class HudLayer(Layer):
    is_event_handler = True
    def __init__(self, game):
        super(HudLayer, self).__init__()
        self.game = game
        
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
        
        self.refresh_current_player()
        
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
        
    def set_info(self, text):
        self.info.do(InfoAction(text, '_', 0.4))

    def on_mouse_press(self, x, y, button, modifiers): 
        x, y = director.get_virtual_coordinates(x, y)
        if self.turn_button.contains(x, y):
            self.end_turn()
            return EVENT_HANDLED
        elif self.influence_layer.click_current_disc(x, y, self.game.current_player):
            self.start_drag_disc(x, y, self.game.current_player.personal_board.influence_track)
            self.influence_layer.refresh(self.game.current_player, False)
            return EVENT_HANDLED

    def start_drag_disc(self, x, y, zone):
        self.influence_disc.color = color_convert(self.game.current_player.color)
        self.influence_disc.visible = True
        self.influence_disc.position = (x, y)
        self.influence_disc_component = zone.take()
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.influence_disc_component is not None:
            self.influence_disc.position = director.get_virtual_coordinates(x, y)
            return EVENT_HANDLED
    
    def on_mouse_release(self, x, y, buttons, modifiers):
        if self.influence_disc_component is not None:
            x, y = director.get_virtual_coordinates(x, y)
            action = self.action_board.get_action_from_coords(x, y)
            if action is not None:
                self.set_info('Select Action: ' + action)
                self.game.current_player.personal_board.action_board.add(action, self.influence_disc_component)
                self.influence_disc_component = None
                self.influence_disc.visible = False
                self.refresh_influence_track()
                self.action_board.refresh(self.game.current_player)
                return EVENT_HANDLED
            self.return_influence_disc()

    def return_influence_disc(self):
        n_influence = len(self.game.current_player.personal_board.influence_track.get_components())
        position = self.influence_layer.get_global_disc_position(n_influence)
        self.game.current_player.personal_board.influence_track.add(self.influence_disc_component)
        self.influence_disc.do(MoveTo(position, duration = 0.5) + Hide(duration = 0.01))
        
    def draw(self):
        if self.influence_disc_component is not None and not self.influence_disc.visible:
            self.influence_disc_component = None
            self.refresh_influence_track()
        super(HudLayer, self).draw()

    def end_turn(self):
        self.game.end_turn()
        self.refresh_current_player()
        
    def refresh_current_player(self):
        self.turn_button.color = color_convert(self.game.current_player.color)
        self.action_board.refresh(self.game.current_player)
        self.refresh_influence_track()
            
    def refresh_influence_track(self):
        self.influence_layer.refresh(self.game.current_player)

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
            if not self.action_sprites.has_key(action):
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
    def __init__(self, game):
        super(BoardScene, self).__init__()
        self.add(ColorLayer(0, 0, 0, 255), 0)
        scroller = ScrollingManager()
        self.hud_layer = HudLayer(game)
        self.popup_layer = PopUpLayer(game)
        self.board_layer = BoardLayer(scroller, self.hud_layer, game)
        scroller.add(self.board_layer)
        self.add(scroller, 1)
        # self.add(control_layer, 2)
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
        
class PlayerBoardScene(Scene):
    def __init__(self, player):
        super(PlayerBoardScene, self).__init__()
        self.add(ColorLayer(200, 200, 200, 255), 0)
        self.add(PlayerBoardLayer(player), 1)
        self.player = player
        # self.add(control_layer, 2)
        
class ResearchBoardScene(Scene):
    def __init__(self):
        super(ResearchBoardScene, self).__init__()
        self.add(ColorLayer(100, 100, 100, 255), 0)
        self.add(ResearchBoardLayer(), 1)
        # self.add(control_layer, 2)
        
class MainScreen(object):
    def __init__(self, game):
        control_layer = ControlLayer(game)
        
        board_scene = BoardScene(game)
        control_layer.add_scene(board_scene, B)
        
        for n, player in enumerate(game.players):
            scene = PlayerBoardScene(player)
            control_layer.add_scene(scene, _1 + n)
            
        research_board_scene = ResearchBoardScene()
        control_layer.add_scene(research_board_scene, R)
        
        director.replace(ZoomTransition(board_scene, 1.0))
        
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
