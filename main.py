from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang.builder import Builder
from kivy.uix.floatlayout import FloatLayout


KV = '''
Board:
    Widget:
        canvas:
            Color:
                rgba: .70, .70, .70, 1
            Rectangle:
                pos: root.width/2 - 150, root.height/2 - 150
                size: 300, 300
'''


class Board(FloatLayout):
    pass


class GameApp(App):

    def build(self):
        kv = Builder.load_string(KV)
        return kv


if __name__ == "__main__":
    GameApp().run()
