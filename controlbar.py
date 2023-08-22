import os

from kivy.lang import Builder
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty
from kivy.uix.floatlayout import FloatLayout
from tkinter import Tk, filedialog

Builder.load_file('controlbar.kv')


class ControlBar(FloatLayout):

    manager = ObjectProperty(None)
    frame_box = ObjectProperty(None)
    btn_play = ObjectProperty(None)
    seek_slider = ObjectProperty(None)
    slider_value = NumericProperty(0)

    is_sliding = False
    btn_play_disabled = BooleanProperty(True)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # File selection function
    def load_data(self):    
        # If playing, then pause it
        self.parent.frame_box.play()
        root = Tk()
        root.withdraw()
        file_name = filedialog.askopenfilename(filetypes= [("Video Files","*.mp4 *.mkv *.mov *.avi")])
        root.destroy()
        if file_name:
            if os.path.exists(file_name):
                self.manager.video_file = file_name
                # Enable the play button
                self.btn_play_disabled = False
                # Reset the state of frame box
                with self.frame_box.condition:
                    self.frame_box.state = 'stop'
                    self.frame_box.condition.notify_all()
                self.frame_box.display_preview()
            else:
                print('Selected file does not exist')

    # Callback when slider is released
    def on_slide_up(self, *args):
        # Do the action only when the slider was pressed
        if self.is_sliding and args[0] == self.seek_slider:
            try:
                # Notify the frame box object and pass the new slider value
                self.parent.frame_box.on_seek(self.seek_slider.value)
            except Exception as e:
                print (f'on_slide_up: {e}')
            finally:
                self.is_sliding = False

    # Callback when slider is pressed
    def on_slide_down(self, *args):
        if args[0].collide_point(*args[1].pos):
            if args[0] == self.seek_slider:
                try:
                    # Set sliding flag
                    self.is_sliding = True
                    # Notify the video capture object to stop capturing
                    self.parent.frame_box.on_slide_down()
                except Exception as e:
                    print (f'on_slide_down: {e}')

    # Function to be called from frame box object to update the slider position
    def update_slider_pos(self, pos):
        self.slider_value = pos

    # Callback function for buttons press event
    def button_press_callback(self, btn):
        if btn == self.btn_play:
            # Play button is pressed
            pass
    
    # Callback function for buttons release event
    def button_release_callback(self, btn):
        if btn == self.btn_play:
            # Play button is released
            self.parent.frame_box.play()
