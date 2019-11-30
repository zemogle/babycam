#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response, send_from_directory
import socket
from glob import glob

from camera import Camera

app = Flask(__name__)


@app.route('/video/<path:path>')
def send_video(path):
    return send_from_directory('video', path)

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html', name=socket.gethostname())

@app.route('/videos/')
def videos():
    """ Timelapse list """
    filelist = [x.split('/')[-1] for x in glob('video/*.mp4')]
    return render_template('videos.html', name=socket.gethostname())

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/latest.jpg')
def latest_image():
    ''' Static image snapshot, useful for timelapse '''
    return Response(Camera().get_frame(), mimetype='image/jpeg')

@app.route('/stream.mjpg')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, port=8000)
