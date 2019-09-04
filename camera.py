import io
import time
import picamera
from datetime import datetime
from fractions import Fraction

from base_camera import BaseCamera


class Camera(BaseCamera):
    @staticmethod
    def frames():
        with picamera.PiCamera(resolution='1296x730', framerate=1) as camera:
            # let camera warm up
            if datetime.now().hour > 18 or datetime.now().hour < 7:
                camera.iso = 800
                camera.exposure_mode = 'off'
                camera.awb_mode = 'off'
                camera.awb_gains = (Fraction(19, 16), Fraction(143, 128))
                camera.shutter_speed = 800000
            else:
                camera.iso = 100
                camera.exposure_mode = 'auto'
                camera.awb_mode = 'auto'
                camera.shutter_speed = 100000
            camera.vflip = True
            camera.hflip = True
            time.sleep(2)

            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # return current frame
                stream.seek(0)
                yield stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()
