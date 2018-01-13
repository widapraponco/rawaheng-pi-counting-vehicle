#!/usr/bin/env python
from importlib import import_module
import time
import os
from _global import get_server_time
from flask import Flask, request, render_template, Response

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera_vehicle_counter import Camera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)

#start counting vehicle
camera_source = Camera()
#counter = 0

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    #global camera_source
    #camera_source = camera
    while True:
        frame = camera.get_frame()
        #counter = camera.get_counter()
        #print(str(counter))
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    #camera.set_video_source("../Assets/flow.avi")
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(camera_source),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_data')
def get_data():
    global camera_source
    if camera_source is None:
         return "0|0|0";
    print("vehicle counter: "+str(camera_source.get_counter()))
    print("browser time: ", request.args.get("time"))
    #print("server time: "), time.strftime('%A %B, %d %Y %H:%M:%S')
    now = get_server_time()
    return str(camera_source.get_counter())+"|"+str(camera_source.get_counter_inaday())+"|"+time.strftime('%A %B, %d %Y %H:%M:%S') 
    ###str(now.hour)+":"+str(now.minute)+":"+str(now.second)### 
    #time.strftime('%A %B, %d %Y %H:%M:%S')

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
