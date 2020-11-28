"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""

import cv2
from gaze_tracking import GazeTracking
from datetime import datetime

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
working = True

work_time = int(input("Enter the number of minutes you want to work for\n")) * 60

break_time = int(input("Enter the number of minutes you want to rest for\n")) * 60

start_time = datetime.now()

while True:
    # We get a new frame from the webcam
    _, frame = webcam.read()
    if working:
        #check eyes on screen
        x = 1 #placeholder
    else:
        #check eyes off screen
        x = 1 #placeholder

    current_time = datetime.now()
    if (working and (current_time - start_time).total_seconds() >= work_time 
    or not working and (current_time - start_time).total_seconds() >= break_time):
        if working and (current_time - start_time).total_seconds() < work_time + 15:
            print("Work about to end, take a rest!")
        elif not working and (current_time - start_time).total_seconds() < break_time + 15:
            print("Work about to start, get to work!")
        else:
            working = not working
            start_time = datetime.now()
    # We send this frame to GazeTracking to analyze it
    gaze.refresh(frame)

    frame = gaze.annotated_frame()
    text = ""

    if gaze.is_blinking():
        text = "Blinking"
    elif gaze.is_right():
        text = "Looking right"
    elif gaze.is_left():
        text = "Looking left"
    elif gaze.is_center():
        text = "Looking center"
        
    cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()
    cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

    cv2.imshow("Demo", frame)

    if cv2.waitKey(1) == 27:
        break
