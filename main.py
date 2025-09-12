from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang.builder import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window


Window.size = (400, 700)


KV = '''
Board:
    Widget:
        pos_hint: {"center_x": .5, "center_y": .5}
        size_hint: None, None
        size: 300, 300
        canvas:
            Color:
                rgba: .70, .70, .70, 1
            Rectangle:
                pos: self.pos
                size: self.size
'''


class Board(FloatLayout):
    pass


class GameApp(App):

    def build(self):
        kv = Builder.load_string(KV)
        return kv


if __name__ == "__main__":
    GameApp().run()
