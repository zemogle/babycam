import io
import socket
import struct
import time
import picamera

def start_camera():
  client_socket = socket.socket()
  client_socket.connect(('0.0.0.0', 8000))
  connection = client_socket.makefile('wb')
  try:
      with picamera.PiCamera() as camera:
          camera.resolution = (640, 480)
          camera.framerate = 30
          time.sleep(2)
          start = time.time()
          stream = io.BytesIO()
          # Use the video-port for captures...
          for foo in camera.capture_continuous(stream, 'jpeg',
                                               use_video_port=True):
              connection.write(struct.pack('<L', stream.tell()))
              connection.flush()
              stream.seek(0)
              connection.write(stream.read())
              if time.time() - start > 30:
                  break
              stream.seek(0)
              stream.truncate()
      connection.write(struct.pack('<L', 0))
  finally:
      connection.close()
      client_socket.close()

if __name__ == '__main__':
  start_camera()
