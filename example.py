"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""

import cv2
from gaze_tracking import GazeTracking
from datetime import datetime
from tkinter import *
from time import sleep, time

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
working = True
screen_size = []

work_time = 20 # int(input("Enter the number of minutes you want to work for\n")) * 60
break_time = 20 # int(input("Enter the number of minutes you want to rest for\n")) * 60

root = Tk()
root.attributes('-fullscreen', True)
root.update_idletasks()
w = root.winfo_screenwidth()
h = root.winfo_screenheight()
root.bind("<Escape>", lambda e: e.widget.quit())

coords = [(10, 10, 30, 30), (w-10, h-10, w-40, h-40) ]

canvas =  Canvas(root, bg='black', width=w, height=h)
canvas.pack()

def callabirate():
    global temp
    instrct = canvas.create_text(w/2,h/2,fill="White", text="Look at the blue dot")
    for i in coords:
        temp = canvas.create_oval(i, outline='blue', fill='blue')
        _, frame = webcam.read()
        gaze.refresh(frame)
        frame = gaze.annotated_frame()
        screen_size.append(gaze.horizontal_ratio())
        screen_size.append(gaze.vertical_ratio())
        root.after(1000, canvas.delete(temp))

    canvas.delete(instrct)

def delete(a):
    canvas.delete(a)

def main():
    working = True
    start_time = datetime.now()
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
    
    warning = ""
    _, frame = webcam.read()
    gaze.refresh(frame)
    frame = gaze.annotated_frame()

    h_ratio = gaze.horizontal_ratio()
    v_ratio = gaze.vertical_ratio()

    try:
        if (h_ratio < screen_size[0] or h_ratio > screen_size[2]) or (v_ratio > screen_size[1] or v_ratio < screen_size[3]):
            warning = canvas.create_text(w/2,h/2,fill="White", text="You aren't looking in the middle")
    except:
        print("ERROR")

    #sleep(3)
    #canvas.delete(warning)
    root.after(100, lambda: delete(warning))
    root.after(3, main)

callabirate()
main()

root.mainloop()