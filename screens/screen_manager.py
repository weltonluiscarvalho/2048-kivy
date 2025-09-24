from kivy.uix.screenmanager import ScreenManager


class GameScreenManager(ScreenManager):

    def load_board_screen(self, state):
        self.ids.board_screen.new_game = state
        self.current = "board_screen"
