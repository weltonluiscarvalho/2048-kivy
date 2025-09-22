from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.core.text import LabelBase
from screens.screen_items import Board
from screens.screens import GameScreenManager, BoardScreen

Window.size = (400, 700)

class GameApp(MDApp):
    pass


if __name__ == "__main__":
    LabelBase.register('clear-sans', 
                       fn_regular='fonts/ClearSans-Regular.ttf', 
                       fn_bold='fonts/ClearSans-Bold.ttf', 
                       fn_bolditalic='fonts/ClearSans-BoldItalic.ttf',
                       fn_italic='fonts/ClearSans-Italic.ttf')
    app = GameApp()
    print(app.user_data_dir)
    app.run()
