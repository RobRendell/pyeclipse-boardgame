__author__="jglouis"
__date__ ="$Dec 21, 2011 10:35:50 AM$"

def constants(*sequential):
    enums = dict(zip(sequential, sequential))
    return type('Constants', (), enums)

UIAction = constants('show_hex_map', 'select_unexplored_hex', 'select_from_hex', 'rotate_reject_hex', 'draw_2_hexes',
                'colony_ship_refresh', 'move_influence_disc',
                'show_research_board', 'buy_tech',
                'show_blueprints', 'add_ship_part',
                'build_unit',
                'move_ship')

actions = {}

class Action(object):
    """
    Action represents the action that a player can take,
    mainly during the action phase.
    """
    def next(self, ui_state, state, game):
        """
        next is called by the UI to advance to the next state in the action.  It returns
        None if the action is complete, or a string indicating some input required from the user.
        """
        pass

class Explore1(Action):
    unexplored_key = 'unexplored hexes'
    selected_key = 'selected'
    from_hex_key = 'from hex'

    def next(self, ui_state, state, game):
        if ui_state == 1:
            return UIAction.show_hex_map
        elif ui_state == 2:
            state[self.unexplored_key] = game.board.get_exploration_options_for(game.current_player)
            return UIAction.select_unexplored_hex
        elif ui_state == 3:
            coords = state[self.selected_key]
            state[self.from_hex_key] = game.board.get_explore_source_hex(game.current_player, coords)
            return UIAction.select_from_hex
        elif ui_state == 4:
            coords = state[self.selected_key]
            sector_tile = game.draw_hex(coords)
            sector = game.place_hex(sector_tile, coords)
            while not game.board.has_wormhole_connection(state[self.from_hex_key][0], coords, game.current_player):
                sector.rotate()
            return UIAction.rotate_reject_hex

class Explore2(Explore1):
    def next(self, ui_state, state, game):
        if ui_state >= 5:
            return super(Explore2, self).next(ui_state - 3, state, game)
        else:
            return super(Explore2, self).next(ui_state, state, game)

class Explore1_1(Explore1):
    def next(self, ui_state, state, game):
        if ui_state == 4:
            return UIAction.draw_2_hexes
        else:
            return super(Explore1_1, self).next(ui_state, state, game)

class Influence(Action):
    def next(self, ui_state, colony_repeat, disc_repeat, state, game):
        if ui_state == 1:
            return UIAction.show_hex_map
        elif ui_state <= 1 + colony_repeat:
            # TODO game.current_player. unflip colony ships or increment "free colonisations'
            return UIAction.colony_ship_refresh
        elif ui_state <= 1 + colony_repeat + disc_repeat:
            return UIAction.move_influence_disc

class Influence2_2(Influence):
    def next(self, ui_state, state, game):
        return super(Influence2_2, self).next(ui_state, 2, 2, state, game)

class Research(Action):
    def next(self, ui_state, repeat, state, game):
        if ui_state == 1:
            return UIAction.show_research_board
        elif ui_state <= 1 + repeat:
            return UIAction.buy_tech

class Research1(Research):
    def next(self, ui_state, state, game):
        return super(Research1, self).next(ui_state, 1, state, game)

class Research2(Research):
    def next(self, ui_state, state, game):
        return super(Research2, self).next(ui_state, 2, state, game)

class Upgrade(Action):
    def next(self, ui_state, repeat, state, game):
        if ui_state == 1:
            return UIAction.show_blueprints
        elif ui_state <= 1 + repeat:
            return UIAction.add_ship_part

class ReactionUpgrade(Upgrade):
    reaction = True
    def next(self, ui_state, state, game):
        return super(ReactionUpgrade, self).next(ui_state, 1, state, game)

class Upgrade2(Upgrade):
    def next(self, ui_state, state, game):
        return super(Upgrade2, self).next(ui_state, 2, state, game)

class Upgrade3(Upgrade):
    def next(self, ui_state, state, game):
        return super(Upgrade3, self).next(ui_state, 3, state, game)

class Build(Action):
    def next(self, ui_state, repeat, state, game):
        if ui_state == 1:
            return UIAction.show_hex_map
        elif ui_state <= 1 + repeat:
            return UIAction.build_unit

class ReactionBuild(Build):
    reaction = True
    def next(self, ui_state, state, game):
        return super(ReactionBuild, self).next(ui_state, 1, state, game)

class Build2(Build):
    def next(self, ui_state, state, game):
        repeat = 2 + game.current_player.get_extra_build_count()
        return super(Build2, self).next(ui_state, repeat, state, game)

class Build3(Build):
    def next(self, ui_state, state, game):
        repeat = 3 + game.current_player.get_extra_build_count()
        return super(Build3, self).next(ui_state, repeat, state, game)

class Move(Action):
    def next(self, ui_state, repeat, state, game):
        if ui_state == 1:
            return UIAction.show_hex_map
        elif ui_state <= 1 + repeat:
            return UIAction.move_ship

class ReactionMove(Move):
    reaction = True
    def next(self, ui_state, state, game):
        return super(ReactionMove, self).next(ui_state, 1, state, game)

class Move2(Move):
    def next(self, ui_state, state, game):
        return super(Move2, self).next(ui_state, 2, state, game)

class Move3(Move):
    def next(self, ui_state, state, game):
        return super(Move3, self).next(ui_state, 3, state, game)

actions['explore1'] = Explore1()
actions['explore2'] = Explore2()
actions['explore1_1'] = Explore1_1()

actions['influence2_2'] = Influence2_2()

actions['research1'] = Research1()
actions['research2'] = Research2()

actions['reaction_upgrade'] = ReactionUpgrade()
actions['upgrade2'] = Upgrade2()
actions['upgrade3'] = Upgrade3()

actions['reaction_build'] = ReactionBuild()
actions['build2'] = Build2()
actions['build3'] = Build3()

actions['reaction_move'] = ReactionMove()
actions['move2'] = Move2()
actions['move3'] = Move3()
