import io
import cv2 as cv
import numpy as np
import time
from functools import partial

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.video import Video
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.graphics.texture import Texture 
from threading import Thread


Builder.load_file('framebox.kv')


class FrameBox(Video):

    manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.texture = Texture.create()
        self.state = "stop"

    # Video Frame Event Function
    def _on_video_frame(self, *largs):
        super()._on_video_frame(*largs)
        time.sleep(0.5)

    def play(self):
        self.source = self.manager.video_file
        self.reload()
        self.texture = Texture.create()
        self.state = "play"