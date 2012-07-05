'''
Created on 4 janv. 2012

@author: jglouis
'''
from cocos.scene import Scene
from cocos.layer.base_layers import Layer
from cocos.text import Label
from cocos.director import director
from cocos.scenes.transitions import FadeUpTransition
from cocos.layer.util_layers import ColorLayer
from cocos.draw import Line
import math
from cocos.layer.scrolling import ScrollableLayer, ScrollingManager
import pyglet
from cocos.sprite import Sprite
from hexmanager import HexManager
from cocos.actions.base_actions import IntervalAction
import random
from engine.zone import Sector, ResourceSlot
from engine.component import InfluenceDisc, Ship, Interceptor, Cruiser,\
    AncientShip, GalacticCenterDefenseSystem, DiscoveryTile, PopulationCube
from pyglet.window.mouse import RIGHT
from pyglet.event import EVENT_HANDLED
from cocos.rect import Rect
from pyglet.window.key import B, R, _1, P, MOD_CTRL
from cocos.batch import BatchNode
from cocos.actions.interval_actions import Rotate
from cocos.menu import Menu, MenuItem, zoom_in, zoom_out, shake, ColorMenuItem, fixedPositionMenuLayout, LEFT, TOP,\
    BOTTOM, verticalMenuLayout

pyglet.resource.path.append('./image')
pyglet.resource.path.append('./image/boards')
pyglet.resource.path.append('./image/diplomats')
pyglet.resource.path.append('./image/discovery_tiles')
pyglet.resource.path.append('./image/upgrade_tiles')
pyglet.resource.path.append('./image/research_tiles')
pyglet.resource.path.append('./image/npc')
pyglet.resource.path.append('./image/ships')
pyglet.resource.path.append('./font')
pyglet.resource.reindex()

pyglet.font.add_directory('font')
    
def color_convert(text):
    return {'blank'     :(255,255,255),
            'red'       :(255,0,0), 
            'green'     :(0,255,0),  
            'blue'      :(0,0,255), 
            'yellow'    :(255,255,0),
            'grey'      :(150,150,150),
            'black'     :(50,50,50),
            'money'     :(212,100,4),
            'material'  :(136,72,41),
            'science'   :(230,146,161),
            None        :(255,255,255)
            }[text]

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
        #extract all the selectable sprite from *args
        super(PopUpSprite, self).__init__('tech_background.png', anchor = (0,0), scale = 2)
        
        self.add(PopulationChoiceMenu(game, board_layer, resource_slot_sprite, player))        
        
class BackgroundSprite(Sprite):
    pass   

class PopulationChoiceMenu(Menu):
    def __init__(self, game, board_layer, resource_slot_sprite, player):
        super(PopulationChoiceMenu, self).__init__()
        items = [
                 MenuItem('money',     self.on_money),
                 MenuItem('material',  self.on_material),
                 MenuItem('science',   self.on_science)
                 ]
        
        self.menu_valign = BOTTOM
        self.menu_halign = LEFT
        
        self.game = game
        self.board_layer = board_layer
        self.resource_slot_sprite = resource_slot_sprite
        self.player = player
        
        self.create_menu(items, layout_strategy=verticalMenuLayout)
        
    def decorator(f):
        def new_f(self):
            if len(self.resource_slot_sprite.obj.get_components()) == 1: #remove population cube                
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
                self.resource_slot_sprite.add(population_sprite,1)       
            self.kill()      
        return new_f
    
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
        #self.add(Sprite(pyglet.resource.image('milkyway.jpg'), scale = 0.5, position = (self.px_width / 2, self.px_height / 2)), -1)
        #self.add(Sprite(pyglet.resource.animation('planet.gif'), scale = 0.5, position = (self.px_width / 2, self.px_height / 2)))
        self.hex_width = 200
        self.hex_manager = HexManager(self.hex_width, (self.px_width / 2, self.px_height / 2))
        self.scroller = scroller
        self.scroller.set_focus(self.px_width / 2, self.px_height / 2)
        self.hud_layer = hud_layer
        self.game = game
        self.hex_color_sprites = {}

        self.batch1 = BatchNode()
        self.batch2 = BatchNode()
        self.batch3 = BatchNode()
        self.add(self.batch1, 1)
        self.add(self.batch2, 2)
        self.add(self.batch3, 3)
        
        for coord in self.game.board.get_components().iterkeys():
            self.display_sector(coord)
    
    def set_hex_color(self, coord, color):
        color = color_convert(color)
        if coord in self.hex_color_sprites:
            self.hex_color_sprites[coord].color = color
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
        
        #hex_color
        try:
            color = sector.get_components(InfluenceDisc)[0].color
        except:
            color = 'grey'
        self.set_hex_color(coord, color)

        #wormholes
        wormhole_positions = [(0.5, 0.5),
                              (0.5, 0),
                              (0, -0.5),
                              (-0.5, -0.5),
                              (-0.5, 0),
                              (0, 0.5)
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
               
        #ships
        for ship in sector.get_components(Ship):
            
            #change that into a dictionary
            
            if isinstance(ship, Interceptor):
                ship_picture = 'interceptor.png'
            elif isinstance(ship, Cruiser):
                ship_picture = 'cruiser.png'
                
                
            ship_coord = self.hex_manager.get_sprite_coord(u, v)
            ship_sprite = SelectableSprite(ship,
                                           ship_picture,
                                           scale = 0.2,
                                           position = ship_coord,
                                           color = color_convert(ship.color)
                                           )
            self.batch1.add(ship_sprite)
            
        #planets
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
            for slot, position in zip(slots, [(x - 10, y),(x + 10, y)]):
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
                
        #vp
        vp = sector.victory_points
        vp_picture = {1 :'reputation1.png',
                      2 :'reputation2.png',
                      3 :'reputation3.png',
                      4 :'reputation4.png'}[vp]
        vp_sprite = Sprite(vp_picture,
                           position = rect_position,
                           scale = 0.2)
        self.batch1.add(vp_sprite)
        
        #artifact
        if sector.artifact:
            artifact_sprite = Sprite('artifact.png',
                                     position = rect_position,
                                     scale = 0.5
                                     )
            artifact_sprite.x += 10
            artifact_sprite.y += 10
            self.batch1.add(artifact_sprite)
        
        #discovery
        if len(sector.get_components(DiscoveryTile)):
            discovery_tile_sprite = Sprite('discovery_tile_back.png',
                                           position = rect_position,
                                           scale = 0.3
                                           )
            self.batch2.add(discovery_tile_sprite)
        
        #ancients and gdc (npc)
        n_ancients = len(sector.get_components(AncientShip))
        for n in range(n_ancients):
            ancient_sprite = Sprite('ancient_ship.png',
                                    position = rect_position,
                                    scale = 0.3
                                    )
            ancient_sprite.x +=  20.0 * (n - (1.0 * n / n_ancients))
            ancient_sprite.y +=  20.0 * (n - (1.0 * n / n_ancients))
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
        
        #Selectable sprite
        for child in self.batch1.get_children() + self.batch2.get_children() + self.batch3.get_children():            
            if isinstance(child, SelectableSprite):
                if child.get_AABB().contains(x, y):
                    if isinstance(child.obj, ResourceSlot) and button == RIGHT and len(sector.get_components(InfluenceDisc)):                        
                        #if it is a wild resource slot, then ask the player which material it is
                        if child.obj.resource_type is None:
                            player = sector.get_components(InfluenceDisc)[0].owner
                            popup = PopulationChoiceMenu(self.game, self, child, player)                                                        
                            popup.position = self.get_ancestor(ScrollingManager).pixel_to_screen(x, y)                            
                            popup_layer = self.get_ancestor(BoardScene).popup_layer                                                        
                            popup_layer.add(popup)
                        
                        elif len(child.obj.get_components()) == 1: #remove population cube
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
                            child.add(population_sprite,1)
                        return EVENT_HANDLED
                    
                    elif isinstance(child.obj, Ship):
                        print child.obj.get_stats()
                        self.hud_layer.update_fleet([child.obj])
                        

        #explore the sector if right click and sector empty
        #influence the sector if right click and not empty
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
                self.hud_layer.set_info('Influence on sector '+ sector.name)
            else:
                player = sector.get_components(InfluenceDisc)[0].owner
                self.game.move(sector, player.personal_board.influence_track, component_type = InfluenceDisc)
                self.set_hex_color(coord, 'grey')
                self.hud_layer.set_info('Influence removed from Sector')                
        elif sector is not None:
            self.hud_layer.set_info(str(sector))
        else:
            self.hud_layer.set_info('Unknown Sector')
            
        return EVENT_HANDLED
                
    def on_mouse_motion(self, x, y, dx, dy):    
        x, y = self.scroller.pixel_from_screen(x,y)
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
        hex_coord.append((hex_centre[0],                hex_centre[1] + 2 * hex_r / math.sqrt(3)))
        hex_coord.append((hex_centre[0] + hex_r,        hex_centre[1] + hex_r / math.sqrt(3)))
        hex_coord.append((hex_centre[0] + hex_r,        hex_centre[1] - hex_r / math.sqrt(3)))
        hex_coord.append((hex_centre[0],                hex_centre[1] - 2 * hex_r / math.sqrt(3)))
        hex_coord.append((hex_centre[0] - hex_r,        hex_centre[1] - hex_r / math.sqrt(3)))
        hex_coord.append((hex_centre[0] - hex_r,        hex_centre[1] + hex_r / math.sqrt(3)))       
        w = 3        
        line1 = Line(hex_coord[0], hex_coord[1],(255,255,255,255) , w)
        line2 = Line(hex_coord[1], hex_coord[2],(255,255,255,255) , w)
        line3 = Line(hex_coord[2], hex_coord[3],(255,255,255,255) , w)
        line4 = Line(hex_coord[3], hex_coord[4],(255,255,255,255) , w)
        line5 = Line(hex_coord[4], hex_coord[5],(255,255,255,255) , w)
        line6 = Line(hex_coord[5], hex_coord[0],(255,255,255,255) , w)
        self.add(line1, 2)
        self.add(line2, 2)
        self.add(line3, 2)
        self.add(line4, 2)
        self.add(line5, 2)
        self.add(line6, 2)   
        
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.scroller.scale += scroll_y * 0.1
        self.scroller.scale = min(max(self.scroller.scale, 0.2), 2)
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers ):
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
        position = (width/2, height/2)
        picture_name = 'player_board_' +\
                        player.color +\
                        ('_terran' if 'terran' in player.faction.name else '_alien') +\
                        '.jpg'
        player_board_sprite = BackgroundSprite(picture_name,
                                     position = position                              
                                     )
        self.add(player_board_sprite)
        self.scale = min(1.0 * width / player_board_sprite.image.width, 1.0 * height / player_board_sprite.image.height)
        #defining the rectangular zone
        self.rect_player_board = player_board_sprite.get_AABB()
        #width, heigth = self.rect_player_board.size ----> bug ?
        width = self.rect_player_board.width
        height = self.rect_player_board.height
        x, y = self.rect_player_board.bottomleft        
        
        self.rect_influence = Rect(x + 0.106 * width, 
                                   y + 0.076 * height, 
                                   width * 0.725, 
                                   height * 0.07)
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
        #erase all sprites but the background
        for child in self.get_children():
            if isinstance(child, Sprite) and not isinstance(child, BackgroundSprite):
                child.kill()
        #influence track        
        n_influence = len(self.player.personal_board.influence_track.get_components())
        for n in range(n_influence):
            position = self.get_influence_coord(n)
            influence_sprite = Sprite('influence white.png',
                                      position = position,
                                      color = self.color,
                                      scale =  0.9)
            self.add(influence_sprite, 2)
            
        #population track(s)
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
        #horizontal lines
        for n in range(nh):
            x1 = rect.left
            x2 = rect.right
            y = rect.bottom + 1.0 * n / nh * rect.height
            a = (x1, y)
            b = (x2, y)
            self.add(Line(a,b,(255,255,255,255)),2)
        #vertical lines
        for n in range(nv):
            x = rect.left + 1.0 * n / nv * rect.width
            y1 = rect.top
            y2 = rect.bottom
            a = (x, y1)
            b = (x, y2)
            self.add(Line(a,b,(255,255,255,255)),2)
        
    def draw_rect(self, rect):   
        for line in ((rect.topleft,     rect.topright), 
                     (rect.topright,    rect.bottomright),
                     (rect.bottomright, rect.bottomleft),
                     (rect.bottomleft,  rect.topleft)):
            self.add(Line(line[0], line[1], (255,255,255,255)), 2)
            
    def on_mouse_press (self, x, y, button, modifiers):
        x, y = director.get_virtual_coordinates(x, y)
        print self.rect_player_board.contains(x,y)
        
class ResearchBoardLayer(Layer):
    is_event_handler = True
    def __init__(self):
        super(ResearchBoardLayer, self).__init__()
        width, height = director.get_window_size()
        position = (width/2, height/2)
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
    def __init__(self,game):
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
        
class HudLayer(Layer):
    is_event_handler = True
    def __init__(self, game):
        super(HudLayer, self).__init__()
        self.game = game
        self.action_board_sprite = Sprite('action_board_terran.png', scale = 0.3)
        self.add(self.action_board_sprite)
        self.action_board_sprite.position = self.action_board_sprite.get_AABB().topleft
        self.action_board_sprite.x += director.get_window_size()[0]
        self.action_list = ('Explore',
                            'Influence',
                            'Research',
                            'Upgrade',
                            'Build',
                            'Move'
                            )
        self.action_position = [0.2, 1.12, 2.05, 3, 3.95, 4.9]
        self.selection_sprite = Sprite('action_selection_halo.png', scale = 0.3, position = self.action_board_sprite.position)
        
        self.turn_button = Sprite('turn_button.png', 
                                  anchor = (0,0),
                                  color = color_convert(game.current_player.color)
                                  )
        
        self.add(self.turn_button)
                
        #message        
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
        
        #fleet manager
        fleet_manager_size = (919, 1252)
        self.fleet_manager_frame = Sprite('fleet_manager.png', (director.get_window_size()[0],director.get_window_size()[1]), scale = 0.5, anchor = fleet_manager_size )
        self.add(self.fleet_manager_frame)
        
    def update_fleet(self, ships):
        #refresh the frame
        for child in self.fleet_manager_frame.get_children():
            child.kill()
        
        #get all the owners
        owners = set([ship.owner for ship in ships])
        for owner in owners:        
            ship_types = set([ship.name for ship in ships if ship.owner is owner])
            for n, ship_type in enumerate(ship_types):               
            
                scale = 0.7
                fleet_manager_size = (919, 1252)
                y_pos = -250 - 300 * n
                ship_sprite = Sprite(ship_type + '.png', (-fleet_manager_size[0] + 200, y_pos), scale = scale, color = color_convert(owner.color))   
                
                self.fleet_manager_frame.add(ship_sprite)

    def update_time(self, dt):
        new_color = [0, random.randint(230,255), 0, 255]       
        self.info.element.color = new_color
        
    def set_info(self, text):
        self.info.do(InfoAction(text, '_', 0.4))

    def on_mouse_press(self, x, y, button, modifiers): 
        rect = self.action_board_sprite.get_AABB()        
        x, y = director.get_virtual_coordinates(x, y)
        if rect.contains(x, y):
            dx = (rect.right - rect.left) / 6.0
            for n in range(6):
                if rect.left + dx * n < x < rect.left + dx * (n + 1):
                    self.parent.hud_layer.set_info('Select Action: ' + self.action_list[n])
                    self.add(self.selection_sprite)
                    self.selection_sprite.x = rect.left + (self.action_position[n] + 0.5) * dx 
                    self.selection_sprite.color = color_convert(self.game.current_player.color)
                    return EVENT_HANDLED
                
        elif self.turn_button.get_AABB().contains(x, y):
            self.game.end_turn()
            self.turn_button.color = color_convert(self.game.current_player.color)
            return EVENT_HANDLED
                   
class PopUpLayer(Layer):
    """
    Layer that is meant to contain pop up menus. When a pop up menu appears, all keypad/mouse events are intercepted
    and won't be propagated to the lower layers.
    """
    is_event_handler = True
    def __init__(self, game):
        super(PopUpLayer, self).__init__()
        self.game = game
        self.is_active = False #will be set to True if a pop up appears. This variable is used to test if the events are to be propagated through the lower layers
        
    def add(self, child, z=0, name=None):
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
        self.add(ColorLayer(0,0,0,255), 0)
        scroller = ScrollingManager()
        self.hud_layer = HudLayer(game)
        self.popup_layer = PopUpLayer(game)
        self.board_layer = BoardLayer(scroller, self.hud_layer, game)
        scroller.add(self.board_layer)
        self.add(scroller, 1)
        #self.add(control_layer, 2)
        self.add(self.hud_layer, 4)
        self.add(self.popup_layer, 5)
        
class PlayerBoardScene(Scene):
    def __init__(self, player):
        super(PlayerBoardScene, self).__init__()
        self.add(ColorLayer(200,200,200,255), 0)
        self.add(PlayerBoardLayer(player), 1)
        self.player = player
        #self.add(control_layer, 2)
        
class ResearchBoardScene(Scene):
    def __init__(self):
        super(ResearchBoardScene, self).__init__()
        self.add(ColorLayer(100,100,100,255), 0)
        self.add(ResearchBoardLayer(), 1)
        #self.add(control_layer, 2)
        
class MainScreen(object):
    def __init__(self, game):  
        director.init(fullscreen = True, resizable = True, do_not_scale = False)
        control_layer = ControlLayer(game)
        
        board_scene = BoardScene(game)
        control_layer.add_scene(board_scene, B)
        
        for n, player in enumerate(game.players):
            scene = PlayerBoardScene(player)
            control_layer.add_scene(scene, _1 + n)
            
        research_board_scene = ResearchBoardScene()
        control_layer.add_scene(research_board_scene, R)
        
        director.run(board_scene)
        
class InfoAction(IntervalAction):
    """Action that can be applied to any Label to make a dynamic text display
    """
    def init(self, word, post_text, duration ):
        self.duration = duration    #: Duration in seconds
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
