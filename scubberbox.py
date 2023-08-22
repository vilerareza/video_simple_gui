from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout


Builder.load_file('scrubberbox.kv')


class ScrubberBox(FloatLayout):

    manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
