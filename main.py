from kivy.app import App
from kivy.clock import Clock
from kivy.core import window
from kivy.uix.widget import Widget
from kivy.lang.builder import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import ListProperty
from random import randint

Window.size = (400, 700)


class Piece(Label):
    position = ListProperty()


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

    def go_up(self):
        for piece in self.children:
            print(f'position before = {piece.position}')
            self.positions[piece.position[0]][piece.position[1]] = 0
            piece.top = piece.parent.top
            piece.position = (piece.position[0], 3)
            print(f'position after = {piece.position}')
        self.insert_piece()

    def go_down(self):
        for piece in self.children:
            print(piece.position)
            piece.y = piece.parent.y
        self.insert_piece()

    def go_left(self):
        for piece in self.children:
            print(piece.position)
            piece.x = piece.parent.x
        self.insert_piece()

    def go_right(self):
        for piece in self.children:
            print(piece.position)
            piece.right = piece.parent.right
        self.insert_piece()

    def insert_piece(self):
        x = randint(0, 3)
        y = randint(0, 3)
        pos_x = x * 75 + self.x
        pos_y = y * 75 + self.y
        new_piece = Piece()
        new_piece.position = (x, y)
        new_piece.pos = (pos_x, pos_y)
        new_piece.size_hint = None, None
        new_piece.size = 75, 75
        self.add_widget(new_piece)
        self.positions[x][y] = 1

class GameApp(App):
    pass


if __name__ == "__main__":
    GameApp().run()
