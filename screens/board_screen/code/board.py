from copy import copy, deepcopy
import enum
from math import ceil
from kivy.app import App
from kivy.uix.modalview import ModalView
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.core.audio import SoundLoader
from kivy.properties import NumericProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from random import choice
from functools import partial, reduce
from datetime import datetime
from database import game_db

from . import Piece

scores = JsonStore('scores.json')

class GameOverPopup(ModalView):
    pass

class Board(MDRelativeLayout):

    num_rows = NumericProperty(4)
    num_columns = NumericProperty(4)
    score = NumericProperty(0)
    best = NumericProperty(0)

    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)
        self.positions = []
        self.in_game = False
        self.in_animation = False
        # self.reset_state()
        # self.initialize_board()
        self.load_sounds()
        self.config_game_over_popup()
        App.get_running_app().bind(on_stop=self.save_moves)
        Window.bind(on_key_down=self.on_key_down)

    def on_score(self, *args):
        base_best = reduce(max, map(lambda timestamp: scores.get(timestamp)['score'], scores.keys()), 0)
        if self.score > base_best:
            self.best = self.score
        else:
            self.best = base_best

    def config_game_over_popup(self):
        self.popup = GameOverPopup()
        self.popup.ids.undo_button.bind(on_release=lambda args: self.on_popup_game_over("undo"))
        self.popup.ids.new_game_button.bind(on_release=lambda args: self.on_popup_game_over("new_game"))
        self.popup.ids.quit_game_button.bind(on_release=lambda args: self.on_popup_game_over("quit_game"))

    def load_sounds(self):
        self.sounds = {}
        self.sounds["ele_gosta"] = SoundLoader.load('assets/sounds/ele_gosta.mp3') 
        self.sounds["ui"] = SoundLoader.load('assets/sounds/ui.mp3') 
        self.sounds["nossa"] = SoundLoader.load('assets/sounds/nossa.mp3') 
        self.sounds["cavalo"] = SoundLoader.load('assets/sounds/cavalo.mp3') 
        self.sounds["danca_gatinho"] = SoundLoader.load('assets/sounds/danca_gatinho.mp3') 

    def initialize_board(self):
        self.game_id = game_db.insert_game()
        self.reset_state()
        new_piece = self.create_new_piece()
        self.insert_piece(new_piece)

    def set_in_animation_false(self, *args):
        self.in_animation = False

    def set_in_animation_true(self, *args):
        self.in_animation = True
        

    def on_popup_game_over(self, button):
        self.in_game= True
        self.popup.dismiss()
        if button == "undo":
            self.undo_move()
        elif button == "new_game":
            self.reset_game()
        else:
            self.quit_game()


    def save_moves(self, *args):
        scores.put(ceil(int(datetime.now().timestamp())), score=self.score, moves=self.moves)
        for row, row_value in enumerate(self.positions):
            for column, piece in enumerate(row_value):
                if piece:
                    game_db.insert_board(self.game_id, row, column, piece.value)


    def save_state(self):
        scores.put(ceil(int(datetime.now().timestamp())), score=self.score, moves=self.moves)


    def reset_state(self):
        for row, row_value in enumerate(self.positions):
            for column, piece_value in enumerate(row_value):
                if piece_value:
                    self.remove_widget(self.positions[row][column])

        self.in_animation = False
        self.in_game = True
        self.moves = []
        self.moves_count = 0
        self.do_moves_count = 0
        self.undo_moves_count = 0
        self.score = 0
        self.best = reduce(max, map(lambda timestamp: scores.get(timestamp)['score'], scores.keys()), 0)

        rows = []
        for i in range(4):
            column = []
            for j in range(4):
                column.append(0)
            rows.append(column)

        self.positions = rows

    def load_state(self):
        if scores.keys():
            last_timestamp = reduce(max, map(lambda timestamp: int(timestamp), scores.keys()))
            self.in_animation = False
            self.in_game = True
            self.score = scores.get(str(last_timestamp))['score']
            self.moves = scores.get(str(last_timestamp))['moves']
            if self.moves:
                last_move = None
                for move in self.moves:
                    if move.get('move_number') == reduce(max, map(lambda move: move.get("move_number"), self.moves), 0):
                        last_move = move

                if last_move:
                    self.moves_count = last_move.get("move_number", 0)
                    self.do_moves_count = last_move.get("do_move_number", 0)
                    self.undo_moves_count = last_move.get("undo_move_number", 0)
                    self.positions = deepcopy(last_move.get("board_after"))
                    print(f'o ultimo board salvo foi {self.positions}')
                    self.fill_board()
            else:
                self.initialize_board()
        else:
            self.initialize_board()

    def fill_board(self):

        for row, row_value in enumerate(self.positions):
            for column, piece_value in enumerate(row_value):
                if piece_value:
                    piece = Piece(value=piece_value)
                    piece.pos_hint={'x': column * .25, 'y': row * .25}
                    piece.coords = (row, column)
                    self.insert_piece(piece)

    def quit_game(self, *args):
        self.save_moves()
        app = App.get_running_app()
        app.stop()


    def reset_game(self, *args):
        scores.put(ceil(int(datetime.now().timestamp())), score=self.score, moves=self.moves)
        self.score = 0
        for row, row_value in enumerate(self.positions):
            for column, piece in enumerate(row_value):
                if piece:
                    self.remove_widget(self.positions[row][column])
                    self.positions[row][column] = 0

        new_piece = self.create_new_piece()
        self.insert_piece(new_piece)
        self.popup.dismiss()
        self.in_game = True
        best = reduce(max, map(lambda timestamp: scores.get(timestamp)['score'], scores.keys()), 0)
        self.best = best


    def can_merge_somepiece(self):

        for row, row_value in enumerate(self.positions):

            for column, piece in enumerate(row_value):
                if piece and self.can_piece_merge(self.positions[row][column]):
                    return True

        return False


    def can_piece_merge(self, piece):

        if piece.coords[0] > 0:
            lower_piece = self.positions[piece.coords[0] - 1][piece.coords[1]]

            if lower_piece and lower_piece.value == piece.value:
                return True

        if piece.coords[0] < 3:
            uper_piece = self.positions[piece.coords[0] + 1][piece.coords[1]]

            if uper_piece and uper_piece.value == piece.value:
                return True

        if piece.coords[1] > 0:
            left_piece = self.positions[piece.coords[0]][piece.coords[1] - 1]

            if left_piece and left_piece.value == piece.value:
                return True

        if piece.coords[1] < 3:
            right_piece = self.positions[piece.coords[0]][piece.coords[1] + 1]

            if right_piece and right_piece.value == piece.value:
                return True

        return False


    def get_pieces_at_column(self, column):
        pieces = []
        for row in range(self.num_rows):
            if self.positions[row][column]:
                pieces.append(self.positions[row][column])
        return pieces

    def get_pieces_at_row(self, row):
        pieces = []
        for column in range(self.num_columns):
            if self.positions[row][column]:
                pieces.append(self.positions[row][column])
        return pieces


    def get_piece_at_position(self, row, column):
        for item in self.children:
            if type(item) is Piece and item.coords[0] == row and item.coords[1] == column:
                return item


    def on_key_down(self, window, key, scancode, codepoint, modifiers):

        if not self.in_animation and self.in_game:

            if key == 273:
                self.move("up")
                
            if key == 274:
                self.move("down")

            if key == 276:
                self.move("left")

            if key == 275:
                self.move("right")

    def unmerge_piece(self, piece_to_unmerge, new_piece_position):
        new_value = int(piece_to_unmerge.value / 2)

        new_row = new_piece_position[0]
        new_column = new_piece_position[1]

        new_piece = Piece(value=new_value)
        new_piece.coords = (new_row, new_column)
        new_piece.pos_hint = {'x': piece_to_unmerge.coords[1] * .25, 'y': piece_to_unmerge.coords[0] * .25}
        new_piece.size_hint = .25, .25
        piece_to_unmerge.change_value(new_value)

        self.add_widget(new_piece)
        anim = Animation(pos_hint={'x': new_column * .25, 'y': new_row * .25}, duration=.15)
        anim.start(new_piece)
        self.positions[new_piece_position[0]][new_piece_position[1]] = new_piece

        self.score -= new_piece.value

        
    def merge_pieces(self, dt, piece_to_merge, piece_merging):
        new_value = piece_to_merge.value * 2
        piece_to_merge.change_value(new_value)
        self.score += piece_merging.value
        if piece_merging.value == 8:
            if self.sounds.get("cavalo"):
                self.sounds.get("cavalo").play()
                self.sounds.get("cavalo").seek(0)
        elif piece_merging.value >= 16:
            if self.sounds.get("nossa"):
                self.sounds.get("nossa").play()
                self.sounds.get("nossa").seek(0)
        self.remove_widget(piece_merging)


    def undo_move(self):
        if self.in_animation or not self.in_game:
            return

        move_to_undo = game_db.select_last_do_move(self.game_id, self.do_moves_count)
        
        if move_to_undo:
            # remove created piece first
            removed_piece = self.positions[move_to_undo['row']][move_to_undo['column']]
            self.positions[move_to_undo['row']][move_to_undo['column']] = 0
            self.remove_widget(removed_piece)

            #undos
            move_direction = move_to_undo["direction"]
            moves = game_db.select_pieces_move_from_move(self.game_id, move_to_undo['move_number'])

            if moves:
                if move_direction in ("up", "right"):
                    range_initial_value = 0
                    range_final_value = self.num_rows
                    range_step_value = 1

                else: 
                    range_initial_value = self.num_rows - 1
                    range_final_value = -1
                    range_step_value = -1

                if move_direction in ("up", "down"):
                    line_type = "row"

                else:
                    line_type = "column"

                for line in range(range_initial_value, range_final_value, range_step_value):

                    line_merges = [move for move in moves if move["final_position"][line_type] == line and move['is_merge']]
                    line_moved_pieces = [move for move in moves if move["final_position"][line_type] == line and not move['is_merge']]

                    # undo merges
                    for move in line_merges:
                        piece_to_unmerge = self.positions[move['final_position']['row']][move['final_position']['column']]
                        self.unmerge_piece(piece_to_unmerge, (move['initial_position']['row'], move['initial_position']['column']))

                    # undo moves
                    for move in line_moved_pieces:
                        old_position = move["initial_position"]["row"], move["initial_position"]["column"]
                        new_position = move["final_position"]["row"], move["final_position"]["column"]

                        piece = self.positions[new_position[0]][new_position[1]]
                        self.set_piece_position(piece, old_position)

            
            self.undo_moves_count += 1
            self.do_moves_count -= 1
            self.moves_count += 1
            self.set_in_animation_true()
            game_db.insert_move(self.moves_count, 
                                self.game_id, 
                                "undo", 
                                None, 
                                self.do_moves_count, 
                                self.score, 
                                move_to_undo['row'], 
                                move_to_undo['column'])
            Clock.schedule_once(self.set_in_animation_false, .17)


    def set_piece_position(self, piece, position, merge=False):

        piece_row = piece.coords[0]
        piece_column = piece.coords[1]

        new_position_row = position[0]
        new_position_column = position[1]

        self.positions[piece_row][piece_column] = 0

        ## move logic
        piece.coords = position
        anim = Animation(pos_hint={'x': new_position_column * .25, 'y': new_position_row * .25}, duration=.15)
        anim.start(piece)
        if merge:
            piece_to_merge = self.positions[new_position_row][new_position_column]
            piece_to_merge.has_already_merged = True
            Clock.schedule_once(partial(self.merge_pieces, piece_to_merge=piece_to_merge, piece_merging=piece), .15)
            return

        self.positions[new_position_row][new_position_column] = piece

    def print_board(self):
        for row in range(self.num_rows - 1, -1, -1):
            print(self.positions[row])

        print()

    def add_do_move(self, direction, move_type, moved_pieces, created_piece):

        game_db.insert_move(self.moves_count, 
                            self.game_id, 
                            move_type, 
                            direction, 
                            self.do_moves_count, 
                            self.score, 
                            created_piece.coords[0], 
                            created_piece.coords[1])

        for piece in moved_pieces:
            game_db.insert_piece_move(self.moves_count, 
                                      self.game_id, 
                                      piece['old_position']['row'], 
                                      piece['old_position']['column'], 
                                      piece['new_position']['row'], 
                                      piece['new_position']['column'], 
                                      piece['piece_value'], 
                                      piece['is_merge'])


    def move(self, move_direction):

        moved_pieces = []
        piece_moved = False

        if move_direction in ("up", "right"):
            line_range_initial_value = self.num_rows - 2
            line_range_final_value = -1
            next_line_range_final_value = self.num_rows
            signal = -1

        else: 
            line_range_initial_value = 0
            line_range_final_value = self.num_rows
            next_line_range_final_value = -1
            signal = 1

        if move_direction in ("up", "down"):
            line_ref = 0
            get_pieces_at_line = self.get_pieces_at_row

        else:
            line_ref = 1
            get_pieces_at_line = self.get_pieces_at_column

            
        for line in range(line_range_initial_value, line_range_final_value, signal):
            line_pieces = get_pieces_at_line(line)

            for piece in line_pieces:

                next_position = piece.coords
                merge = False

                for next_line in range(piece.coords[line_ref] - signal, next_line_range_final_value, -signal):

                    row, column = (next_line, piece.coords[1]) if move_direction in ("up", "down") else (piece.coords[0], next_line)

                    piece_at_next_position = self.positions[row][column]

                    if piece_at_next_position:

                        if piece.value == piece_at_next_position.value and not piece_at_next_position.has_already_merged:
                            merge = True
                            next_position = (row, column)
                        break

                    next_position = (row, column)

                if piece.coords is not next_position:
                    piece_moved = True
                    new_move = {
                        "piece_value": piece.value,
                        "old_position": {
                            "row": piece.coords[0],
                            "column": piece.coords[1]
                        },
                        "new_position": {
                            "row": next_position[0],
                            "column": next_position[1]
                        },
                        "is_merge": merge
                    }

                    moved_pieces.append(new_move)

                    self.set_piece_position(piece, next_position, merge=merge)

        for row, row_value in enumerate(self.positions):
            for column, piece in enumerate(row_value):
                if piece:
                    piece.has_already_merged = False

        if piece_moved:
            self.set_in_animation_true()
            new_piece = self.create_new_piece()
            self.moves_count += 1
            self.do_moves_count += 1
            Clock.schedule_once(partial(self.insert_piece, new_piece), .15)
            Clock.schedule_once(partial(self.add_do_move, 
                                        direction=move_direction, 
                                        move_type="do", 
                                        created_piece=new_piece, 
                                        moved_pieces=moved_pieces), .16)
            Clock.schedule_once(self.set_in_animation_false, .17)


    def create_new_piece(self, *args):
        free_positions = []

        for row, row_value in enumerate(self.positions):
            for column, value in enumerate(row_value):
                if not value:
                    free_positions.append((row, column))

        position = choice(free_positions)

        row = position[0]
        column = position[1]

        new_piece = Piece(value=2)
        new_piece.coords = (row, column)
        new_piece.pos_hint = {'x': column * .25, 'y': row * .25}
        return new_piece

    def insert_piece(self, new_piece, *args):
        # if self.moves_count > 5:
        #     self.in_game = False
        #     self.popup.ids.score_label.text = str(self.score)
        #     self.popup.open()

        self.add_widget(new_piece)
        self.positions[new_piece.coords[0]][new_piece.coords[1]] = new_piece
        ### DB
        if self.moves_count == 0:
            game_db.insert_move(self.moves_count, self.game_id, None, None, self.do_moves_count, 0, new_piece.coords[0], new_piece.coords[1])
        ####

        free_positions = []

        for row, row_value in enumerate(self.positions):
            for column, value in enumerate(row_value):
                if not value:
                    free_positions.append((row, column))

        if self.score > self.best:
            self.best = self.score

        if not free_positions and not self.can_merge_somepiece():
            self.in_game = False
            self.popup.ids.score_label.text = str(self.score)
            # self.popup.score = self.score
            self.popup.open()
            return
