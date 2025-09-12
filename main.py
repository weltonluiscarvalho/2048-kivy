from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang.builder import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window


Window.size = (400, 700)


class Board(FloatLayout):
    pass


class GameApp(App):

    def build(self):
        return Board()


if __name__ == "__main__":
    GameApp().run()
