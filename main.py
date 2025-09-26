from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.lang.builder import Builder
from database import game_db

from screens.board_screen.code import BoardScreen
from screens.screen_manager import GameScreenManager

Window.size = (400, 700)

class GameApp(MDApp):

    def on_start(self):
        game_db.open_connection()
        game_db.create_tables()
        game_db.populate_position()
        return super().on_start()

    def on_stop(self):
        game_db.close_connection()
        return super().on_stop()

if __name__ == "__main__":
    LabelBase.register('clear-sans', 
                       fn_regular='assets/fonts/ClearSans-Regular.ttf', 
                       fn_bold='assets/fonts/ClearSans-Bold.ttf', 
                       fn_bolditalic='assets/fonts/ClearSans-BoldItalic.ttf',
                       fn_italic='assets/fonts/ClearSans-Italic.ttf')

    app = GameApp()
    Builder.load_file('screens/main_screen/ui/main_screen.kv')
    Builder.load_file('screens/board_screen/ui/board_screen.kv')
    Builder.load_file('screens/board_screen/ui/board.kv')
    Builder.load_file('screens/board_screen/ui/piece.kv')
    app.run()
