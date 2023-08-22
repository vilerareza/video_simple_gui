import io
import cv2 as cv
import numpy as np
import time
from functools import partial

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.graphics.texture import Texture 
from threading import Thread, Condition


Builder.load_file('framebox.kv')

class FrameBox(Image):

    manager = ObjectProperty(None)
    control_bar = ObjectProperty(None)

    video_cap = None
    video_pos = 0
    video_duration = 0
    seek_event = False
    on_sliding = False
    condition = Condition()
    state = 'stop'


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.texture = Texture.create()


    def play(self):

        if self.state == 'stop':
            # Stop to play
            with self.condition:
                self.state = 'play'
                self.condition.notify_all()
            self.play_thread = Thread(target = self.play_)
            self.play_thread.daemon = True
            self.play_thread.start()

        elif self.state == 'play':
            # Play to pause
            with self.condition:
                self.state = 'pause'
                self.condition.notify_all()
            # Reset play button image and disable it      
            Clock.schedule_once(partial(self.change_play_btn_img, 'images/play.png'), 0)

        elif self.state == 'pause':
            # Pause to play
            with self.condition:
                self.state = 'play'
                self.condition.notify_all()
            # Reset play button image and disable it      
            Clock.schedule_once(partial(self.change_play_btn_img, 'images/pause.png'), 0)


    def play_(self):

        try:
            # Initialize capture object
            self.video_cap = cv.VideoCapture(self.manager.video_file)

            ### Get video properties            
            frame_w = int(self.video_cap.get(cv.CAP_PROP_FRAME_WIDTH))
            frame_h = int(self.video_cap.get(cv.CAP_PROP_FRAME_HEIGHT))
            self.video_fps = self.video_cap.get(cv.CAP_PROP_FPS)
            video_n_frame = self.video_cap.get(cv.CAP_PROP_FRAME_COUNT)
            self.video_duration = (video_n_frame/self.video_fps)*1000
            print (frame_w, frame_h)
            print (f'fps: {self.video_fps}')
            print (f'duration: {self.video_duration}')

            # Measure capture time (as offset to update the frame)
            for i in range (5):
                # Read 1st 5 frame to get stable result
                ret, frame = self.video_cap.read()
            t1 = time.time()
            ret, frame = self.video_cap.read()
            t2 = time.time()
            # Calculate the capture time
            t_capture = t2-t1
            # Resetting the capture position 1st frame again
            self.video_cap.set(cv.CAP_PROP_POS_FRAMES, 1)

            # Calculate adjusted  size (640px target width)
            new_frame_w = 640
            size_factor = new_frame_w/frame_w
            new_frame_h = int(frame_h*size_factor)

            # Creating texture
            self.texture = Texture.create(size=(new_frame_w, new_frame_h), colorfmt="rgb")

            # Update play button image to pause       
            Clock.schedule_once(partial(self.change_play_btn_img, 'images/pause.png'), 0)

        except Exception as e:
            print (e, 'No video is selected or unable to open selected video file..')
            # Reset the playing flag
            self.state = 'stop'
            return


        ### Video Loop
        while (self.video_cap.isOpened()):

            # Check if slider is pressed. Stop if so.
            with self.condition:
                if self.on_sliding or self.state=='pause':
                    self.condition.wait()
                    continue
                elif self.state == 'stop':
                    # Stop
                    # Reset play button image and disable it      
                    Clock.schedule_once(partial(self.change_play_btn_img, 'images/play.png'), 0)
                    # Update slider position
                    self.manager.video_box.control_bar.update_slider_pos(0)
                    # Release video capture object
                    self.video_cap.release()
                    # Create blank texture
                    self.texture = Texture.create()
                    break

            # Reading frame
            t1=time.time()
            ret, frame = self.video_cap.read()

            if ret:
                # Get current time position in mSec
                cur_time_ms = self.video_cap.get(cv.CAP_PROP_POS_MSEC)
                cur_video_pos = (cur_time_ms / self.video_duration)*100

                # Update slider position
                self.manager.video_box.control_bar.update_slider_pos(cur_video_pos)
                # Resize the frame to the adjusted size
                frame = cv.resize(frame, (new_frame_w,new_frame_h))
                frame = frame[:,:,::-1]
                frame = cv.flip(frame,0)
                self.on_frame_(frame)
                cv.waitKey(25 - int(t_capture*1000))
                t2 = time.time()
                #print (f'time: {t2-t1}')

            else:
                print ('End of the stream')
                # Create blank texture
                self.texture = Texture.create()
                # Reset play button image and disable it      
                Clock.schedule_once(partial(self.change_play_btn_img, 'images/play.png'), 0)
                # Reset the playing flag
                self.state = 'stop'
                # Release video capture object
                self.video_cap.release()
                break

    # Update the livestream texture with new frame
    def update_frame(self, buff_, *largs):
        data = buff_.flatten()
        self.texture.blit_buffer(data, bufferfmt="ubyte", colorfmt="rgb")
        self.canvas.ask_update()
    
    # Update the livestream texture with new frame
    def on_frame_(self, img_array):
        Clock.schedule_once(partial(self.update_frame, img_array), 0)

    # Callback when slider is released. Seek the video based on slider position
    def on_seek(self, slider_pos):
        with self.condition:
            if slider_pos==0:
                self.video_cap.set(cv.CAP_PROP_POS_FRAMES, 1)
            else:                
                self.video_pos = self.video_duration*slider_pos/100
                self.video_cap.set(cv.CAP_PROP_POS_MSEC, self.video_pos)
            self.on_sliding = False
            self.condition.notify_all()

    # Callback function when the slider is touched
    def on_slide_down(self):
        with self.condition:
            # Set the flag that the slide is being touched. 
            self.on_sliding = True
            self.condition.notify_all()

    # Change play button appearance
    def change_play_btn_img(self, path, *args):
        self.control_bar.btn_play.source = path

    # Display preview image
    def display_preview(self):
        # Initialize capture object
        preview_video_cap = cv.VideoCapture(self.manager.video_file)
        ### Get video properties            
        frame_w = int(preview_video_cap.get(cv.CAP_PROP_FRAME_WIDTH))
        frame_h = int(preview_video_cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        # Get frame at 1 sec
        preview_video_cap.set(cv.CAP_PROP_POS_FRAMES, 1)
        # Creating texture
        self.texture = Texture.create(size=(frame_w, frame_h), colorfmt="rgb")
        # Read frame
        ret, frame = preview_video_cap.read()
        # Display frame
        frame = frame[:,:,::-1]
        frame = cv.flip(frame,0)
        self.on_frame_(frame)
        # Release
        preview_video_cap.release()
