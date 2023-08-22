import os
from kivy.lang import Builder
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.metrics import dp
from videobox import VideoBox
from scubberbox import ScrubberBox

Builder.load_file('manager.kv')

class Manager(BoxLayout):

    video_box = ObjectProperty()
    scrubber_box = ObjectProperty()
    
    video_file = StringProperty('')
    video_current_pos = NumericProperty(0)

    def stop(self):
        pass