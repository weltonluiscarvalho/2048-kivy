from kivy.uix.label import Label
from kivy.properties import BooleanProperty, ListProperty, ColorProperty, NumericProperty
from color_map import color_map

class Piece(Label):
    color_bg = ColorProperty()
    coords = ListProperty()
    has_already_merged = BooleanProperty(False)
    value = NumericProperty(0)

    def __init__(self, value, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.color_bg = color_map.get(str(value)).get('bg', 'white')
        self.color = color_map.get(str(value)).get('font','black')

    def change_value(self, new_value):
        self.value = new_value
        if new_value >= 4096:
            map_value = "4096"
        else:
            map_value = color_map.get(str(new_value))
        self.color_bg = map_value.get('bg', 'white')
        self.color = map_value.get('font','black')

    def on_value(self, instance, value):
        self.text = str(value)

    def __repr__(self) -> str:
        return str(self.value)
