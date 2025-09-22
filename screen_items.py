import enum
from math import ceil
import os
from kivy.app import App
from kivy.uix.modalview import ModalView
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.core.audio import SoundLoader
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import NumericProperty, BooleanProperty, ListProperty, ColorProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from random import choice
from functools import partial, reduce
from datetime import datetime
from color_map import color_map


scores = JsonStore('scores.json')

class GameOverPopup(ModalView):
    score = NumericProperty(0)

class PositionRectangle(Widget):
    pass

class Piece(Label):
    color_bg = ColorProperty()
    coords = ListProperty()
    has_already_merged = BooleanProperty(False)

    def __init__(self, value, **kwargs):
        self.text = value
        self.color_bg = color_map.get(value).get('bg', 'white')
        self.color = color_map.get(value).get('font','black')
        super().__init__(**kwargs)

    def change_value(self, new_value):
        self.text = new_value
        if int(new_value) >= 4096:
            map_value = "4096"
        else:
            map_value = color_map.get(new_value)
        self.color_bg = map_value.get('bg', 'white')
        self.color = map_value.get('font','black')

    def __repr__(self) -> str:
        return self.text

class Board(MDRelativeLayout):

    num_rows = NumericProperty(4)
    num_columns = NumericProperty(4)
    score = NumericProperty(0)
    best = NumericProperty(0)

    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)
        rows = []
        for i in range(4):
            column = []
            for j in range(4):
                column.append(0)
            rows.append(column)
        self.positions = rows
        self.in_animation = False
        self.in_game = True
        self.ele_gosta = SoundLoader.load('sounds/ele_gosta.mp3')
        self.ui = SoundLoader.load('sounds/ui.mp3')
        self.nossa = SoundLoader.load('sounds/nossa.mp3')
        self.cavalo = SoundLoader.load('sounds/cavalo.mp3')
        self.danca_gatinho = SoundLoader.load('sounds/danca_gatinho.mp3')
        self.popup = GameOverPopup()
        self.popup.ids.undo_button.bind(on_release=lambda args: self.on_popup_game_over("undo"))
        self.popup.ids.new_game_button.bind(on_release=lambda args: self.on_popup_game_over("new_game"))
        self.popup.ids.quit_game_button.bind(on_release=lambda args: self.on_popup_game_over("quit_game"))
        self.moves = []
        self.moves_count = 0
        self.do_moves_count = 0
        self.undo_moves_count = 0
        self.sequential_undo_moves = 0
        self.previous_do_move = 0
        best = reduce(max, map(lambda timestamp: scores.get(timestamp)['score'], scores.keys()), 0)
        self.best = best
        app = App.get_running_app()
        app.bind(on_stop=self.save_moves)
        Clock.schedule_once(self.start, -1)
        Window.bind(on_key_down=self.on_key_down)

    def set_in_animation_false(self, *args):
        self.in_animation = False

    def set_in_animation_true(self, *args):
        self.in_animation = True
        
    def start(self, *args):
        self.insert_black_rectangles()
        new_piece = self.create_new_piece()
        self.insert_piece(new_piece)


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
                    self.positions[row][column] = 0
                    self.remove_widget(piece)

        new_piece = self.create_new_piece()
        self.insert_piece(new_piece)
        self.popup.dismiss()
        self.in_game = True
        best = reduce(max, map(lambda timestamp: scores.get(timestamp)['score'], scores.keys()), 0)
        self.best = best


    def can_merge_somepiece(self):

        for row, row_value in enumerate(self.positions):

            for column, piece in enumerate(row_value):
                if piece and self.can_piece_merge(piece):
                    return True

        return False


    def can_piece_merge(self, piece):

        if piece.coords[0] > 0:
            lower_piece = self.positions[piece.coords[0] - 1][piece.coords[1]]

            if lower_piece and lower_piece.text == piece.text:
                return True

        if piece.coords[0] < 3:
            upon_piece = self.positions[piece.coords[0] + 1][piece.coords[1]]

            if upon_piece and upon_piece.text == piece.text:
                return True

        if piece.coords[1] > 0:
            left_piece = self.positions[piece.coords[0]][piece.coords[1] - 1]

            if left_piece and left_piece.text == piece.text:
                return True

        if piece.coords[1] < 3:
            right_piece = self.positions[piece.coords[0]][piece.coords[1] + 1]

            if right_piece and right_piece.text == piece.text:
                return True

        return False



    def insert_black_rectangles(self):
        for row, row_value in enumerate(self.positions):
            for column, column_value in enumerate(row_value):
                pox = column * self.width / 4
                poy = row * self.width / 4
                r = PositionRectangle(pos=(pox, poy))
                self.add_widget(r)


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
        new_value = str(int(int(piece_to_unmerge.text) / 2))
        self.print_board()

        new_row = new_piece_position[0]
        new_column = new_piece_position[1]
        new_pos_x = new_column * self.width / 4
        new_pos_y = new_row * self.width / 4

        new_piece = Piece(value=new_value)
        new_piece.coords = (new_row, new_column)
        new_piece.pos = piece_to_unmerge.pos
        new_piece.size_hint = .25, .25
        piece_to_unmerge.change_value(new_value)

        self.add_widget(new_piece)
        anim = Animation(pos=(new_pos_x, new_pos_y), duration=.15)
        anim.start(new_piece)
        self.positions[new_piece_position[0]][new_piece_position[1]] = new_piece 
        self.print_board()

        self.score -= int(new_piece.text)

        

    def merge_pieces(self, dt, piece_to_merge, piece_merging):
        new_value = int(piece_to_merge.text) * 2
        piece_to_merge.change_value(str(new_value))
        self.score += int(piece_merging.text)
        if piece_merging.text == "8":
            if self.cavalo:
                self.cavalo.play()
                self.cavalo.seek(0)
        elif int(piece_merging.text) >= 16:
            if self.nossa:
                self.nossa.play()
                self.nossa.seek(0)
        self.remove_widget(piece_merging)
        self.print_board()


    def undo_move(self):
        if self.in_animation or not self.in_game:
            return
        os.system('clear')
        print(f'board from the last move')
        self.print_board()

        move_to_undo = None
        print(f'do moves performed = {self.do_moves_count}')
        print(f'sequential undo moves perfomed = {self.sequential_undo_moves}')
        
        moves_able_to_undo = filter(lambda move: move.get("move_type") == "do" and move.get("do_move_number") == self.do_moves_count, self.moves)
        # print(f'moves able to undo')
        # for move in moves_able_to_undo:
        #     print(move)
        move_to_undo_number = reduce(max, map(lambda move: move.get("move_number"), moves_able_to_undo), 0)
        print(move_to_undo_number)
        for move in self.moves:
            if move.get("move_number") == move_to_undo_number:
                move_to_undo = move
                break
            
        if move_to_undo:
            print(f'move to undo {move_to_undo}')

            # remove created piece first
            print(f'board before remove created piece')
            self.print_board()
            created_piece = move_to_undo.get("created_piece")
            created_piece_position = created_piece.get("position").get("row"), created_piece.get("position").get("column")
            removed_piece = self.positions[created_piece_position[0]][created_piece_position[1]]
            self.positions[created_piece_position[0]][created_piece_position[1]] = 0
            self.remove_widget(removed_piece)
            print(f'board after remove created piece')
            self.print_board()

            move_direction = move_to_undo.get("direction")
            unmerged_pieces = []
            unmoved_pieces = []

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

                line_moved_pieces = [piece for piece in move_to_undo.get("pieces_moved") if piece.get("new_position").get(line_type) == line]
                line_merges = [piece for piece in move_to_undo.get("merges") if piece.get("piece_merged_position").get(line_type) == line]

                #undo merges
                if line_merges:
                    print(f'board before unmerge pieces')
                    self.print_board()
                    print(f'merges to be unmerged {line_merges}')
                for merge in line_merges:

                    merged_position = merge.get("piece_merged_position").get("row"), merge.get("piece_merged_position").get("column")
                    merging_position = merge.get("piece_merging_position").get("row"), merge.get("piece_merging_position").get("column")

                    print(f"a unmerged will be performed for the merge {merge}")
                    print(f'piece to unmerge {merge.get("new_value")}')
                    print(f"piece to unmerge position {merged_position}")
                    print(f'new_piece_position {merging_position}')
                    piece = self.positions[merged_position[0]][merged_position[1]]
                    self.unmerge_piece(piece, merging_position)
                    unmerge = {
                        "old_value": merge.get("new_value"),
                        "new_value": merge.get("old_value"),
                        "old_position": {
                            "row": merged_position[0],
                            "column": merged_position[1]
                        },
                        "new_position": {
                            "row": merging_position[0],
                            "column": merging_position[1]
                        }
                    }
                    unmerged_pieces.append(unmerge)

                # undo moves
                if line_moved_pieces:
                    print(f'board before unmove pieces of {line_type} {line}')
                    self.print_board()
                    print(f'moves to be unmoved {line_moved_pieces}')
                for moved_piece in line_moved_pieces:
                    old_position = moved_piece.get("old_position").get("row"), moved_piece.get("old_position").get("column")
                    new_position = moved_piece.get("new_position").get("row"), moved_piece.get("new_position").get("column")

                    piece = self.positions[new_position[0]][new_position[1]]
                    print(f'move to be unmoved {moved_piece}')
                    self.set_piece_position(piece, old_position)
                    unmove = {
                        "piece_value": moved_piece.get("piece_value"),
                        "old_position": {
                            "row": new_position[0],
                            "column": new_position[1],
                        },
                        "new_position": {
                            "row": old_position[0],
                            "column": old_position[1]
                        }
                    }
                    unmoved_pieces.append(unmove)

                if line_moved_pieces:
                    print(f'board after unmove pieces of {line_type} {line}')
                    self.print_board()


            # self.sequential_undo_moves += 1
            self.undo_moves_count += 1
            self.do_moves_count -= 1
            self.moves_count += 1
            self.set_in_animation_true()
            board_before, board_after = move_to_undo.get("board_after"), move_to_undo.get("board_before")
            Clock.schedule_once(partial(self.add_undo_move, 
                                        board_before=board_before, 
                                        board_after=board_after, 
                                        move_type="undo", 
                                        removed_piece=removed_piece, 
                                        unmerged_pieces=unmerged_pieces, 
                                        unmoved_pieces=unmoved_pieces), .16)
            Clock.schedule_once(self.set_in_animation_false, .17)


    def set_piece_position(self, piece, position, merge=False):
        if merge:
            print('board before merge pieces')
            self.print_board()
            print("a merge will be performed")
            print(f'pieces that will merge value {piece.text}')
            print(f'piece that will merge position {piece.coords}')
            print(f"piece that will be merged position {position}")

        piece_row = piece.coords[0]
        piece_column = piece.coords[1]

        new_position_row = position[0]
        new_position_column = position[1]

        self.positions[piece_row][piece_column] = 0

        ## move logic
        pos_x = new_position_column * self.width / 4
        pos_y = new_position_row * self.width / 4
        piece.coords = position
        anim = Animation(pos=(pos_x, pos_y), duration=.15)
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

    def add_do_move(self, *args, board_before, direction, move_type, merged_pieces, moved_pieces, created_piece):
        board_after = []
        for row, row_value in enumerate(self.positions):
            board_after_column = []
            for piece in row_value:
                  board_after_column.append(int(piece.text) if piece else 0)
            board_after.append(board_after_column)
        

        move = {
            "move_number": self.moves_count,
            "do_move_number": self.do_moves_count,
            "move_score": self.score,
            "direction": direction,
            "move_type": move_type,
            "board_before": board_before,
            "board_after": board_after,
            "merges": merged_pieces,
            "pieces_moved": moved_pieces,
            "created_piece": {
                "value": int(created_piece.text),
                "position": {
                    "row": created_piece.coords[0],
                    "column": created_piece.coords[1]
                }
            }
        }

        print(f'move did')
        print(move)

        self.moves.append(move)

    def add_undo_move(self, *args, board_before, board_after, move_type, unmerged_pieces, unmoved_pieces, removed_piece):
        move = {
            "move_number": self.moves_count,
            "undo_move_number": self.undo_moves_count,
            "move_score": self.score,
            "move_type": move_type,
            "board_before": board_before,
            "board_after": board_after,
            "unmerges": unmerged_pieces,
            "pieces_unmoved": unmoved_pieces,
            "removed_piece": {
                "value": int(removed_piece.text),
                "position": {
                    "row": removed_piece.coords[0],
                    "column": removed_piece.coords[1]
                }
            }
        }

        self.moves.append(move)


    def move(self, move_direction):
        os.system('clear')
        self.sequential_undo_moves = 0

        # if self.do_moves_count > 9:
        #     self.undo_move()
        #     return

        board_before = []
        for row, row_value in enumerate(self.positions):
            board_before_column = []
            for piece in row_value:
                 board_before_column.append(int(piece.text) if piece else 0)
            board_before.append(board_before_column)
        merged_pieces = []
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

                        if piece.text == piece_at_next_position.text and not piece_at_next_position.has_already_merged:
                            merge = True
                            next_position = (row, column)
                        break

                    next_position = (row, column)

                if piece.coords is not next_position:
                    piece_moved = True
                    if merge:
                        new_merge = {
                            "old_value": int(piece.text),
                            "new_value": int(piece.text) * 2,
                            "piece_merging_position": {
                                "row": piece.coords[0],
                                "column": piece.coords[1]
                            },
                            "piece_merged_position": {
                                "row": next_position[0],
                                "column": next_position[1]
                            }
                        }

                        merged_pieces.append(new_merge)
                    else:
                        new_move = {
                            "piece_value": int(piece.text),
                            "old_position": {
                                "row": piece.coords[0],
                                "column": piece.coords[1]
                            },
                            "new_position": {
                                "row": next_position[0],
                                "column": next_position[1]
                            }
                        }

                        moved_pieces.append(new_move)

                    self.set_piece_position(piece, next_position, merge=merge)

        for row, row_value in enumerate(self.positions):
            for column, column_value in enumerate(row_value):
                if column_value:
                    column_value.has_already_merged = False

        if piece_moved:
            self.set_in_animation_true()
            new_piece = self.create_new_piece()
            self.moves_count += 1
            self.do_moves_count += 1
            Clock.schedule_once(partial(self.insert_piece, new_piece), .15)
            Clock.schedule_once(partial(self.add_do_move, 
                                        board_before=board_before, 
                                        direction=move_direction, 
                                        move_type="do", 
                                        created_piece=new_piece, 
                                        merged_pieces=merged_pieces, 
                                        moved_pieces=moved_pieces), .16)
            Clock.schedule_once(self.set_in_animation_false, .17)


    def create_new_piece(self, *args):
        # if self.moves_count > 5:
        #     self.in_game = False
        #     self.popup.score = self.score
        #     self.popup.open()
        free_positions = []

        for row, row_value in enumerate(self.positions):
            for column, value in enumerate(row_value):
                if not value:
                    free_positions.append((row, column))

        position = choice(free_positions)

        row = position[0]
        column = position[1]

        pos_x = column * self.width / 4
        pos_y = row * self.width / 4
        new_piece = Piece(value='2')
        new_piece.coords = (row, column)
        new_piece.pos = (pos_x, pos_y)
        new_piece.size_hint = .25, .25
        self.positions[row][column] = new_piece
        return new_piece

    def insert_piece(self, new_piece, *args):
        self.add_widget(new_piece)

        free_positions = []

        for row, row_value in enumerate(self.positions):
            for column, value in enumerate(row_value):
                if not value:
                    free_positions.append((row, column))

        if self.score > self.best:
            self.best = self.score

        if not free_positions and not self.can_merge_somepiece():
            self.in_game = False
            self.popup.score = self.score
            self.popup.open()
            return


