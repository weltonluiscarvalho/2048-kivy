from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty

class BoardScreen(Screen):
    new_game = BooleanProperty(True)

    def on_pre_enter(self, *args):
        if self.new_game:
            self.ids.board.initialize_board()
        else:
            self.ids.board.reset_state()
            self.ids.board.load_state()
        return super().on_pre_enter(*args)


    def on_leave(self, *args):
        self.ids.board.save_state()
        return super().on_leave(*args)
