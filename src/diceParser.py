# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 03:10:25 2020

@author: tyler
"""
# ESC to read the dice
#returns the total sum

import cv2
import numpy as np
import eventlet
import socketio

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

last_result = -1

cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)  # '0' is the webcam's ID. usually it is 0 or 1. 'cap' is the video object.
cap.set(15, -4)  # '15' references video's brightness. '-4' sets the brightness.

def diceParser():
    
    lastSum = 0
    min_threshold = 10                      # these values are used to filter our detector.
    max_threshold = 200                     # they can be tweaked depending on the camera distance, camera angle, ...
    min_area = 100                          # ... focus, brightness, etc.
    min_circularity = .3
    min_inertia_ratio = .5

    counter = 0                             # script will use a counter to handle FPS.
    readings = [0, 0]                       # lists are used to track the number of pips.
    display = [0, 0]

    keyPointCoord = []

    while True:

        ret, im = cap.read()
        if not ret:
            print("Bad capture device!")
            break

        grayFrame = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        grayFrame = cv2.cvtColor(grayFrame, cv2.COLOR_GRAY2BGR)
        im = grayFrame

        # im = cv2.equalizeHist(grayFrame)
        #grayFrame = cv2.adaptiveThreshold(grayFrame,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
        ret, im = cv2.threshold(grayFrame,115,255,cv2.THRESH_BINARY)
        #ret, im = cv2.threshold(grayFrame,115,255,cv2.THRESH_BINARY_INV)
        # edge detect
        #im = cv2.Canny(thr,100,200) # 'im' will be a frame from the video.



        params = cv2.SimpleBlobDetector_Params()                
        # declare filter parameters.
        params.filterByArea = True
        params.filterByCircularity = True
        params.filterByInertia = True
        params.minThreshold = min_threshold
        params.maxThreshold = max_threshold
        params.minArea = min_area
        params.minCircularity = min_circularity
        params.minInertiaRatio = min_inertia_ratio
        #Very generic params

        detector = cv2.SimpleBlobDetector_create(params)        # create a blob detector 
        keypoints = detector.detect(im)                         # keypoints is a list containing the blobs.
        #array of dice Coords 
        # here we draw keypoints on the frame.
        im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        # # Display cam with drawn points
        # cv2.imshow("Dice Reader", im_with_keypoints)

        if counter >= 500:                # set maximum sizes for variables and lists to save memory.
            counter = 0
            readings = [0, 0]
            display = [0, 0]
            break

        reading = len(keypoints)                                # 'reading' is the number of blobs/pips

        if counter % 10 == 0:                                   # creates a 
            readings.append(reading)                            # note the reading from this frame.

            if readings[-1] == readings[-2] == readings[-3]:    # if the last 3 readings are the same...
                display.append(readings[-1])                    # ... then we have a valid reading.

            # if the most recent valid reading has changed, and it's something other than zero, then print it.
            if display[-1] != display[-2] and display[-1] != 0:
                msg = str(display[-1]) + "\n****"
                lastSum = str(display[-1])
                #print(msg)

            
            keyPointCoord = []
            diceTotal = 0
                
            
            for x in keypoints:
                    
                x0 = str(x.pt[0])
                y0 = str(x.pt[1])
                if diceTotal > 0:
                    if abs(x.pt[0] - float(px)) < 30 or abs(x.pt[1] - float(py)) < 30:
                        #print("test")
                        pass
                    else:
                        keyPointCoord.append([x0,y0])
                        diceTotal = diceTotal + 1
                        px = x0
                        py = y0
                else:
                    keyPointCoord.append([x0,y0])
                    diceTotal = diceTotal + 1
                    #previous x0 and previous y0
                    px = x0
                    py = y0
                    
        
            #for x in keyPointCoord:
                #msg = "x: " + str(keyPointCoord[x][0]) + "y: " + str(keyPointCoord[x][1]) + "\n\n"
                #msg = "x: " + str(x[0]) + "y: " + str(x[1]) + "\n\n"
                    #print(fuck)
                #print(x)
            #print("total dice: " + str(diceTotal) + "\n")
                
            
            #cv2.PutText(im_with_keypoints, str(msg), (45,45), cv2.FONT_HERSHEY_SIMPLEX, (0,0,255))
        counter += 1

        cv2.waitKey()
 
        # k = cv2.waitKey(30) & 0xff                              # press [Esc] to exit.
        # if k == 27:
        #     break
  
    # cv2.destroyAllWindows()
                
    #print(lastSum)
    global last_result
    last_result = lastSum
    return lastSum

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