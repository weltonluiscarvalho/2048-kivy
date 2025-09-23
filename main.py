from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.lang.builder import Builder
from screens.board_screen.code import Board

Window.size = (400, 700)

class GameApp(MDApp):
    pass


if __name__ == "__main__":
    LabelBase.register('clear-sans', 
                       fn_regular='assets/fonts/ClearSans-Regular.ttf', 
                       fn_bold='assets/fonts/ClearSans-Bold.ttf', 
                       fn_bolditalic='assets/fonts/ClearSans-BoldItalic.ttf',
                       fn_italic='assets/fonts/ClearSans-Italic.ttf')

    app = GameApp()
    Builder.load_file('screens/main_screen/ui/screen.kv')
    Builder.load_file('screens/board_screen/ui/screen.kv')
    Builder.load_file('screens/board_screen/ui/board.kv')
    Builder.load_file('screens/board_screen/ui/piece.kv')
    app.run()
