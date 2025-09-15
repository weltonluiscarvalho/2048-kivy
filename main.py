from math import pi
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core import window
from kivy.uix.widget import Widget
from kivy.lang.builder import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import ListProperty, ColorProperty, NumericProperty, BooleanProperty
from random import randint, random, choice
from functools import partial

Window.size = (400, 700)

color_map = {
    "2": (200/255,165/255,245/255),
    "4": (20/255,16/255,45/255),
    "8": (230/255,126/255,45/255),
    "16": (23/255,226/255,235/255),
    "32": (188/255,2/255,9/255),
    "64": (88/255,72/255,99/255),
    "128": (203/255,152/255,199/255),
    "256": (255/255,255/255,4/255),
    "512": (25/255,55/255,244/255),
    "1024": (154/255,200/255,43/255),
    "2048": (14/255,0/255,243/255),
}

class Piece(Label):
    color_bg = ColorProperty()
    coords = ListProperty()
    has_already_merged = BooleanProperty

    def __init__(self, value, **kwargs):
        self.text = value
        self.color_bg = color_map.get(value)
        super().__init__(**kwargs)

    def change_value(self, new_value):
        self.text = new_value
        self.color_bg = color_map.get(new_value)

class Board(FloatLayout):

    num_rows = NumericProperty(4)
    num_columns = NumericProperty(4)

    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)
        rows = []
        for i in range(4):
            column = []
            for j in range(4):
                column.append(0)
            rows.append(column)
        self.positions = rows
        Clock.schedule_once(self.start, -1)
        Window.bind(on_key_down=self.on_key_down)


    def start(self, *args):
        self.insert_piece()


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
        self.remove_widget(piece_merging)

    def set_piece_position(self, piece, position, animate=False, merge=False):

        piece_row = piece.coords[0]
        piece_column = piece.coords[1]

        new_position_row = position[0]
        new_position_column = position[1]

        self.positions[piece_row][piece_column] = None

        ## move logic
        pos_x = new_position_column * 75 + self.x
        pos_y = new_position_row * 75 + self.y
        piece.coords = position
        if animate:
            anim = Animation(pos=(pos_x, pos_y), duration=.15)
            anim.start(piece)
            if merge:
                piece_to_merge = self.positions[new_position_row][new_position_column]
                piece_to_merge.has_already_merged = True
                Clock.schedule_once(partial(self.merge_pieces, piece_to_merge=piece_to_merge, piece_merging=piece), .15)
                return
        else:
            piece.pos = (pos_x, pos_y)

        self.positions[new_position_row][new_position_column] = piece

    def go_up(self):

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
                    self.set_piece_position(piece, next_position, animate=True, merge=merge)

        for row, row_value in enumerate(self.positions):
            for column, column_value in enumerate(row_value):
                if column_value:
                    column_value.has_already_merged = False

        Clock.schedule_once(self.schedule_insert_piece, .3)

    def go_down(self):

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
                    self.set_piece_position(piece, next_position, animate=True, merge=merge)

        for row, row_value in enumerate(self.positions):
            for column, column_value in enumerate(row_value):
                if column_value:
                    column_value.has_already_merged = False

        Clock.schedule_once(self.schedule_insert_piece, .3)

    def go_left(self):

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
                    self.set_piece_position(piece, next_position, animate=True, merge=merge)

        for row, row_value in enumerate(self.positions):
            for column, column_value in enumerate(row_value):
                if column_value:
                    column_value.has_already_merged = False

        Clock.schedule_once(self.schedule_insert_piece, .3)

    def go_right(self):

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
                    self.set_piece_position(piece, next_position, animate=True, merge=merge)

        for row, row_value in enumerate(self.positions):
            for column, column_value in enumerate(row_value):
                if column_value:
                    column_value.has_already_merged = False

        Clock.schedule_once(self.schedule_insert_piece, .3)

    def schedule_insert_piece(self, args):
        self.insert_piece()

    def insert_piece(self):
        free_positions = []

        for row, row_value in enumerate(self.positions):
            for column, value in enumerate(row_value):
                if not value:
                    free_positions.append((row, column))

        if not free_positions:
            print("there is not possible_positions, you lose")
            return

        position = choice(free_positions)

        row = position[0]
        column = position[1]

        pos_x = column * 75 + self.x
        pos_y = row * 75 + self.y
        new_piece = Piece(value='2')
        new_piece.coords = (row, column)
        new_piece.pos = (pos_x, pos_y)
        new_piece.size_hint = None, None
        new_piece.size = 75, 75
        self.add_widget(new_piece)
        self.positions[row][column] = new_piece

class GameApp(App):
    pass


if __name__ == "__main__":
    GameApp().run()
