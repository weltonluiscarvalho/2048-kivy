from kivy.app import App
from kivy.clock import Clock
from kivy.core import window
from kivy.uix.widget import Widget
from kivy.lang.builder import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import ListProperty, ColorProperty
from random import randint, random

Window.size = (400, 700)


class Piece(Label):
    position = ListProperty()
    color_bg = ColorProperty()

    def __init__(self, **kwargs):
        self.color_bg = (random(), random(), random())
        super().__init__(**kwargs)

class Board(FloatLayout):

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

    def on_key_down(self, window, key, scancode, codepoint, modifiers):

        if key == 273:
            self.go_up()
            
        if key == 274:
            self.go_down()

        if key == 276:
            self.go_left()

        if key == 275:
            self.go_right()


    def set_piece_position(self, piece, row, column):
        self.positions[piece.position[0]][piece.position[1]] = 0

        ## move logic
        pos_x = column * 75 + self.x
        pos_y = row * 75 + self.y
        piece.position = (row, column)
        piece.pos = (pos_x, pos_y)

        self.positions[piece.position[0]][piece.position[1]] = 1

    def go_up(self):
        # for piece in self.children:
        #     self.positions[piece.position[0]][piece.position[1]] = 0
        #
        #     piece.top = piece.parent.top
        #
        #     piece.position = (piece.position[0], 3)
        #     self.positions[piece.position[0]][piece.position[1]] = 1
        # self.insert_piece()

        for row in range(2, -1, -1):
            for column in range(4):
                # verify if a piece exists at this position
                if self.positions[row][column]:
                    # verify possible new position for this piece
                    next_row = row
                    for upper_row in range(row + 1, 4):
                        # verify if don't exist a piece at the next upper position
                        if not self.positions[upper_row][column]:
                            next_row = upper_row
                    # find the piece, I know that's horrible, i gonna adjust this logic soon
                    for piece in self.children:
                        if piece.position == [row, column]:
                            self.set_piece_position(piece, row=next_row, column=column)
        self.insert_piece()

    def go_down(self):
        # for piece in self.children:
        #     self.positions[piece.position[0]][piece.position[1]] = 0
        #     piece.y = piece.parent.y
        #     piece.position = (piece.position[0], 0)
        #     self.positions[piece.position[0]][piece.position[1]] = 1
        # self.insert_piece()

        for row in range(1, 4):
            for column in range(4):
                # verify if a piece exists at this position
                if self.positions[row][column]:
                    # verify possible new position for this piece
                    next_row = row
                    for lower_row in range(row - 1, -1, -1):
                        # verify if don't exist a piece at the next lower position
                        if not self.positions[lower_row][column]:
                            next_row = lower_row
                    for piece in self.children:
                        if piece.position == [row, column]:
                            self.set_piece_position(piece, row=next_row, column=column)
        self.insert_piece()

    def go_left(self):
        # for piece in self.children:
        #     self.positions[piece.position[0]][piece.position[1]] = 0
        #     piece.x = piece.parent.x
        #     piece.position = (0, piece.position[1])
        #     self.positions[piece.position[0]][piece.position[1]] = 1
        # self.insert_piece()

        for column in range(1, 4):
            for row in range(4):
                # verify if a piece exists at this position
                if self.positions[row][column]:
                    new_position = (row, column)
                    # verify possible new position for this piece
                    next_column = column
                    for left_column in range(column - 1, -1, -1):
                        # verify if don't exist a piece at the next leftmost column position
                        if not self.positions[row][left_column]:
                            next_column = left_column
                    for piece in self.children:
                        if piece.position == [row, column]:
                            self.set_piece_position(piece, row=row, column=next_column)
        self.insert_piece()

    def go_right(self):
        # for piece in self.children:
        #     self.positions[piece.position[0]][piece.position[1]] = 0
        #     piece.right = piece.parent.right
        #     piece.position = (3, piece.position[1])
        #     self.positions[piece.position[0]][piece.position[1]] = 1
        # self.insert_piece()

        for column in range(2, -1, -1):
            for row in range(4):
                # verify if a piece exists at this position
                if self.positions[row][column]:
                    new_position = (row, column)
                    # verify possible new position for this piece
                    next_column = column
                    for right_column in range(column + 1, 4):
                        # verify if don't exist a piece at the next rightmost column position
                        if not self.positions[row][right_column]:
                            next_column = right_column
                    for piece in self.children:
                        if piece.position == [row, column]:
                            self.set_piece_position(piece, row=row, column=next_column)
        self.insert_piece()

    def insert_piece(self):
        possible_positions = []
        for row in self.positions:
            for column in row:
                if not column:
                    possible_positions.append([row][column])

        if not possible_positions:
            print("there is not possible_positions, you lose")
            return

        while True:
            row = randint(0, 3)
            column = randint(0, 3)
            if not self.positions[row][column]:
                break

        pos_x = column * 75 + self.x
        pos_y = row * 75 + self.y
        new_piece = Piece()
        new_piece.position = (row, column)
        new_piece.pos = (pos_x, pos_y)
        new_piece.size_hint = None, None
        new_piece.size = 75, 75
        self.add_widget(new_piece)
        self.positions[row][column] = 1
        print(self.positions)

class GameApp(App):
    pass


if __name__ == "__main__":
    GameApp().run()
