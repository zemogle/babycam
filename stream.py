import io
import picamera
import logging
import socketserver
import time
from datetime import datetime
from threading import Thread
from threading import Condition
from http import server
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from shutil import copyfile

IMAGE_DIR = "/home/pi/images/"
TIMELAPSE_INTERVAL = 60

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/latest.jpg':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'image/jpeg')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def timestamp_image(filename, timestamp):
    img = Image.open(filename)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("sans-serif.ttf", 16)
    draw.text((0, 0),timestamp,(255,255,255),font=font)
    img.save(filename)
    return

with picamera.PiCamera(resolution='800x600', framerate=10) as camera:
    address = ('0.0.0.0', 8000)
    server = StreamingServer(address, StreamingHandler)
    server_thread = Thread(target=server.serve_forever)
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        server_thread.start()
        while True:
            time.sleep(TIMELAPSE_INTERVAL)
            camera.capture('latest.jpg', use_video_port=True, splitter_port=2)
            timestamp = datetime.now().strftime("%Y%m%d%H%M")
            filename = '{}image{}.jpg'.format(IMAGE_DIR, timestamp)
            copyfile('latest.jpg',filename)
    finally:
        camera.stop_recording()
