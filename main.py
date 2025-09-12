from kivy.app import App
from kivy.core import window
from kivy.uix.widget import Widget
from kivy.lang.builder import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.core.window import Window


Window.size = (400, 700)


class Piece(Label):

    def __init__(self, **kwargs):
        super(Piece, self).__init__(**kwargs)
        Window.bind(on_key_down=self.on_key_down)

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
        if self.top < self.parent.top:
            self.y += 75

    def go_down(self):
        if self.y > self.parent.y:
            self.y -= 75

    def go_left(self):
        if self.x > self.parent.x:
            self.x -= 75

    def go_right(self):
        if self.right < self.parent.right:
            self.x += 75

class Board(FloatLayout):
    pass


class GameApp(App):
    pass


if __name__ == "__main__":
    GameApp().run()
