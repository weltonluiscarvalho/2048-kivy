from kivy.uix.modalview import ModalView
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.core.audio import SoundLoader
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import NumericProperty, BooleanProperty, ListProperty, ColorProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from random import choice
from functools import partial

color_map = {
    "2": {
        "font": "#401d01",
        "bg": "#e3e0d8", 
    },
    "4": {
        "font": "#401d01",
        "bg": "#e6d7b1", 
    },
    "8": {
        "font": "white",
        "bg": "#f5ba7a", 
    },
    "16": {
        "font": "white",
        "bg": "#f5a045", 
    },
    "32": {
        "font": "white",
        "bg": "#f58b7a", 
    },
    "64": {
        "font": "white",
        "bg": "#f55d45", 
    },
    "128": {
        "font": "white",
        "bg": "#f2e279", 
    },
    "256": {
        "font": "white",
        "bg": "#f0db56", 
    },
    "512": {
        "font": "white",
        "bg": "#f2d93d", 
    },
    "1024": {
        "font": "white",
        "bg": "#fadc1e", 
    },
    "2048": {
        "font": "white",
        "bg": "#ffdd05", 
    },
    "4096": {
        "font": "white",
        "bg": "#323232", 
    },
}

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
        map_value = color_map.get(new_value)
        self.color_bg = map_value.get('bg', 'white')
        self.color = map_value.get('font','black')

    def __repr__(self) -> str:
        return self.text

class Board(MDRelativeLayout):

    num_rows = NumericProperty(4)
    num_columns = NumericProperty(4)
    score = NumericProperty(0)

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
        self.popup.ids.new_game_button.bind(on_release=self.reset_game)
        Clock.schedule_once(self.start, -1)
        Window.bind(on_key_down=self.on_key_down)

    def set_in_animation_false(self, *args):
        self.in_animation = False

    def set_in_animation_true(self, *args):
        self.in_animation = True
        
    def start(self, *args):
        self.insert_black_rectangles()
        self.insert_piece()


    def reset_game(self, *args):
        self.score = 0
        for row, row_value in enumerate(self.positions):
            for column, piece in enumerate(row_value):
                if piece:
                    self.positions[row][column] = 0
                    self.remove_widget(piece)

        self.insert_piece()
        self.popup.dismiss()
        self.in_game = True


    def can_merge_somepiece(self):

        for row, row_value in enumerate(self.positions):

            print(f'analizing row {row} which have {row_value} pieces')
            for column, piece in enumerate(row_value):
                print(f'analizing piece {piece} in position {piece.coords}')
                if piece and self.can_piece_merge(piece):
                    print(f'a merge is possible for piece {piece} in position {piece.coords}')
                    return True

        return False


    def can_piece_merge(self, piece):

        if piece.coords[0] > 0:
            lower_piece = self.positions[piece.coords[0] - 1][piece.coords[1]]
            print(f'comparing piece {piece} with piece {lower_piece} in position {lower_piece.coords}')

            if lower_piece and lower_piece.text == piece.text:
                return True

        if piece.coords[0] < 3:
            upon_piece = self.positions[piece.coords[0] + 1][piece.coords[1]]
            print(f'comparing piece {piece} with piece {upon_piece} in position {upon_piece.coords}')

            if upon_piece and upon_piece.text == piece.text:
                return True

        if piece.coords[1] > 0:
            left_piece = self.positions[piece.coords[0]][piece.coords[1] - 1]
            print(f'comparing piece {piece} with piece {left_piece} in position {left_piece.coords}')

            if left_piece and left_piece.text == piece.text:
                return True

        if piece.coords[1] < 3:
            right_piece = self.positions[piece.coords[0]][piece.coords[1] + 1]
            print(f'comparing piece {piece} with piece {right_piece} in position {right_piece.coords}')

            if right_piece and right_piece.text == piece.text:
                return True

        print(f'piece {piece} in position {piece.coords} is not able to perform a merge')
        self.print_board()
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
                self.go_up()
                
            if key == 274:
                self.go_down()

            if key == 276:
                self.go_left()

            if key == 275:
                self.go_right()

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

    def set_piece_position(self, piece, position, animate=False, merge=False):

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
        # anim.bind(on_start=self.set_in_animation_true)
        # anim.bind(on_complete=self.set_in_animation_false)
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

    def go_up(self):

        piece_moved = False

        for row in range(self.num_rows - 2, -1, -1):
            row_pieces = self.get_pieces_at_row(row)

            for piece in row_pieces:

                next_position = piece.coords
                merge = False

                for next_row in range(piece.coords[0] + 1, self.num_rows):

                    piece_at_next_position = self.positions[next_row][piece.coords[1]]

                    if piece_at_next_position:

                        if piece.text == piece_at_next_position.text and not piece_at_next_position.has_already_merged:
                            merge = True
                            next_position = (next_row, piece.coords[1])
                        break

                    next_position = (next_row, piece.coords[1])

                if piece.coords is not next_position:
                    piece_moved = True
                    self.set_piece_position(piece, next_position, animate=True, merge=merge)

        for row, row_value in enumerate(self.positions):
            for column, column_value in enumerate(row_value):
                if column_value:
                    column_value.has_already_merged = False

        if piece_moved:
            self.set_in_animation_true()
            Clock.schedule_once(self.insert_piece, .15)
            Clock.schedule_once(self.set_in_animation_false, .16)

    def go_down(self):

        piece_moved = False
        for row in range(self.num_rows):
            row_pieces = self.get_pieces_at_row(row)

            for piece in row_pieces:

                next_position = piece.coords
                merge = False

                for next_row in range(piece.coords[0] - 1, -1, -1):

                    piece_at_next_position = self.positions[next_row][piece.coords[1]]

                    if piece_at_next_position:

                        if piece.text == piece_at_next_position.text and not piece_at_next_position.has_already_merged:
                            merge = True
                            next_position = (next_row, piece.coords[1])
                        break

                    next_position = (next_row, piece.coords[1])

                if piece.coords is not next_position:
                    piece_moved = True
                    self.set_piece_position(piece, next_position, animate=True, merge=merge)

        for row, row_value in enumerate(self.positions):
            for column, column_value in enumerate(row_value):
                if column_value:
                    column_value.has_already_merged = False

        if piece_moved:
            self.set_in_animation_true()
            Clock.schedule_once(self.insert_piece, .15)
            Clock.schedule_once(self.set_in_animation_false, .16)

    def go_left(self):

        piece_moved = False
        for column in range(self.num_columns):
            column_pieces = self.get_pieces_at_column(column)

            for piece in column_pieces:

                next_position = piece.coords
                merge = False

                for next_column in range(piece.coords[1] - 1, -1, -1):

                    piece_at_next_position = self.positions[piece.coords[0]][next_column]

                    if piece_at_next_position:

                        if piece.text == piece_at_next_position.text and not piece_at_next_position.has_already_merged:
                            merge = True
                            next_position = (piece.coords[0], next_column)

                        break

                    next_position = (piece.coords[0], next_column)

                if piece.coords is not next_position:
                    piece_moved = True
                    self.set_piece_position(piece, next_position, animate=True, merge=merge)

        for row, row_value in enumerate(self.positions):
            for column, column_value in enumerate(row_value):
                if column_value:
                    column_value.has_already_merged = False

        if piece_moved:
            self.set_in_animation_true()
            Clock.schedule_once(self.insert_piece, .15)
            Clock.schedule_once(self.set_in_animation_false, .16)

    def go_right(self):

        piece_moved = False
        for column in range(self.num_columns - 2, -1, -1):
            column_pieces = self.get_pieces_at_column(column)

            for piece in column_pieces:

                next_position = piece.coords
                merge = False

                for next_column in range(piece.coords[1] + 1, self.num_columns):

                    piece_at_next_position = self.positions[piece.coords[0]][next_column]

                    if piece_at_next_position:

                        if piece.text == piece_at_next_position.text and not piece_at_next_position.has_already_merged:
                            merge = True
                            next_position = (piece.coords[0], next_column)

                        break

                    next_position = (piece.coords[0], next_column)

                if piece.coords is not next_position:
                    piece_moved = True
                    self.set_piece_position(piece, next_position, animate=True, merge=merge)

        for row, row_value in enumerate(self.positions):
            for column, column_value in enumerate(row_value):
                if column_value:
                    column_value.has_already_merged = False

        if piece_moved:
            self.set_in_animation_true()
            Clock.schedule_once(self.insert_piece, .15)
            Clock.schedule_once(self.set_in_animation_false, .16)

    def insert_piece(self, *args):
        # self.in_game = False
        # self.popup.score = self.score
        # self.popup.open()
        free_positions = []

        for row, row_value in enumerate(self.positions):
            for column, value in enumerate(row_value):
                if not value:
                    free_positions.append((row, column))

        if not free_positions:
            print('there is no free positions, you lose')
            return

        position = choice(free_positions)

        row = position[0]
        column = position[1]

        pos_x = column * self.width / 4
        pos_y = row * self.width / 4
        new_piece = Piece(value='2')
        new_piece.coords = (row, column)
        new_piece.pos = (pos_x, pos_y)
        new_piece.size_hint = .25, .25
        self.add_widget(new_piece)
        self.positions[row][column] = new_piece

        free_positions = []

        for row, row_value in enumerate(self.positions):
            for column, value in enumerate(row_value):
                if not value:
                    free_positions.append((row, column))

        if not free_positions and not self.can_merge_somepiece():
            print('there is no free positions, neither merge to be performed, you lose')
            self.in_game = False
            self.popup.score = self.score
            self.popup.open()
            return
