# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 03:10:25 2020

@author: tyler
"""
# ESC to read the dice
# returns the total sum

import cv2
import eventlet
import socketio

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

last_result = -1

cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)  # '0' is the webcam's ID. usually it is 0 or 1. 'cap' is the video object.
cap.set(15, -4)  # '15' references video's brightness. '-4' sets the brightness.


def diceParser():
    min_threshold = 0  # these values are used to filter our detector.
    max_threshold = 255  # they can be tweaked depending on the camera distance, camera angle, ...
    min_area = 40  # ... focus, brightness, etc.
    max_area = 1000
    min_circularity = 0.5
    min_inertia_ratio = 0.5

    counter = 0  # script will use a counter to handle FPS.

    while True:

        ret, im = cap.read()

        # good ole 'croppin
        im = im[120:480, 120:520]

        if not ret:
            print("Bad capture device!")
            break

        grayFrame = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        grayFrame = cv2.equalizeHist(grayFrame)  # accounts for lighting

        ret, im = cv2.threshold(grayFrame, 240, 255, cv2.THRESH_TOZERO)

        params = cv2.SimpleBlobDetector_Params()
        # declare filter parameters.
        params.filterByArea = True
        params.filterByCircularity = True
        params.filterByInertia = True
        params.filterByConvexity = False  # very important!
        params.minThreshold = min_threshold
        params.maxThreshold = max_threshold
        params.minArea = min_area
        params.maxArea = max_area
        params.minCircularity = min_circularity
        params.minInertiaRatio = min_inertia_ratio

        detector = cv2.SimpleBlobDetector_create(params)  # create a blob detector
        keypoints = detector.detect(im)  # keypoints is a list containing the blobs.

        counter += 1

        if counter >= 3:  # let a couple frames pass to stabilize
            return len(keypoints)


@sio.event
def connect(sid, environ):
    print('connection established')
    global last_result
    if last_result != -1:
        sio.emit('receive_dice', last_result)


@sio.event
def get_dice(sid):
    result = diceParser()
    print(result)
    sio.emit('receive_dice', result)


@sio.event
def disconnect(sid):
    print('disconnected from server')


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5005)), app)
