from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core import window
from kivy.uix.widget import Widget
from kivy.lang.builder import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import ListProperty, ColorProperty, NumericProperty, ObjectProperty
from random import randint, random, choice

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


class Position(Widget):

    row = NumericProperty()
    column = NumericProperty()

    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.piece = None

    def __repr__(self):
        return f"Position(row={self.row}, column={self.column}, piece={self.piece})"


class Piece(Label):
    color_bg = ColorProperty()
    coords = ListProperty()

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
        self.matrix_positions = []
        rows = []
        for i in range(4):
            column = []
            for j in range(4):
                column.append(0)
                self.matrix_positions.append(Position(row=i, column=j))
            rows.append(column)
        self.positions = rows
        Clock.schedule_once(self.start, -1)
        Window.bind(on_key_down=self.on_key_down)

    def start(self, *args):
        self.insert_piece()


    def merge_pieces(self, piece_to_merge, piece_merging):
        pass


    def get_most_longest_free_position(self, position, direction):

        position_row = position[0]
        position_column = position[1]
        next_longest_free_position = position

        if direction is 'up':
            for row in range(position_row, self.num_rows):
                if not self.positions[row][position_column]:
                    next_longest_free_position = (row, position_column)

        elif direction is 'down':
            for row in range(position_row, -1, -1):
                if not self.positions[row][position_column]:
                    next_longest_free_position = (row, position_column)

        elif direction is 'left':
            for column in range(position_column, -1, -1):
                if not self.positions[position_row][column]:
                    next_longest_free_position = (position_row, column)

        else:
            for column in range(position_column, self.num_columns):
                if not self.positions[position_row][column]:
                    next_longest_free_position = (position_row, column)

        return next_longest_free_position if next_longest_free_position is not position else False

        
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


    def set_piece_position(self, piece, position, animate=False):

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
        else:
            piece.pos = (pos_x, pos_y)

        self.positions[new_position_row][new_position_column] = piece

    def go_up(self):

        for row in range(self.num_rows - 2, -1, -1):
            this_row_pieces = self.get_pieces_at_row(row)

            for piece in this_row_pieces:
                new_position = self.get_most_longest_free_position(piece.coords, 'up')
                if new_position:
                    self.set_piece_position(piece, new_position, animate=True)

        Clock.schedule_once(self.schedule_insert_piece, .3)

    def go_down(self):

        for row in range(self.num_rows):
            this_row_pieces = self.get_pieces_at_row(row)

            for piece in this_row_pieces:
                new_position = self.get_most_longest_free_position(piece.coords, 'down')
                if new_position:
                    self.set_piece_position(piece, new_position, animate=True)

        Clock.schedule_once(self.schedule_insert_piece, .3)

    def go_left(self):

        for column in range(self.num_columns):
            this_column_pieces = self.get_pieces_at_column(column)

            for piece in this_column_pieces:
                new_position = self.get_most_longest_free_position(piece.coords, 'left')
                if new_position:
                    self.set_piece_position(piece, new_position, animate=True)

        Clock.schedule_once(self.schedule_insert_piece, .3)

    def go_right(self):

        for column in range(self.num_columns - 2, -1, -1):
            this_column_pieces = self.get_pieces_at_column(column)

            for piece in this_column_pieces:
                new_position = self.get_most_longest_free_position(piece.coords, 'right')
                if new_position:
                    self.set_piece_position(piece, new_position, animate=True)

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

        print(f'the free position choosen is {position}')

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
