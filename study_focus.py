import cv2
from gaze_tracking import GazeTracking
from tkinter import *
from time import sleep
from datetime import datetime
from focus_callabirate import Callibrate

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)

callabirator = Callibrate()
callabirator.calibrate()
screen_size = callabirator.get_screen_size()

window2 = Tk()
window2.attributes('-fullscreen', True)
window2.update_idletasks()
w = window2.winfo_screenwidth()
h = window2.winfo_screenheight()
canvas2 =  Canvas(window2, bg='black', width=w, height=h)
canvas2.pack()
window2.withdraw()

success = canvas2.create_text(w/2, h/2, fill="White", text="YOU ARE NOT LOOKING AT THE SCREEN")

window2.bind("<Escape>", lambda e: e.widget.quit())

bad_count = 0
bad_process = False

def main():
    global success
    global bad_count

    _, frame = webcam.read()
    gaze.refresh(frame)
    frame = gaze.annotated_frame()

    h_ratio = gaze.horizontal_ratio()
    v_ratio = gaze.vertical_ratio()

    print(h_ratio)
    print(v_ratio)
    print(screen_size)

    if h_ratio and v_ratio:
        if (1.2*h_ratio < screen_size[0] or h_ratio > 1.2*screen_size[2]) or (1.2*v_ratio  < screen_size[1] or v_ratio > 1.2*screen_size[3]) and not gaze.is_blinking():
            bad_count = bad_count + 1
            if bad_count > 5:
                window2.deiconify()
                print("Print please")
                print(bad_count)
                canvas2.itemconfigure(success, text="YOU ARE NOT LOOKING AT THE SCREEN")
            elif bad_process:
                window2.deiconify()
                canvas2.itemconfigure(success, text="YOU ARE DOING SOMETHING NAUGHTY")
        elif (1.2*h_ratio > screen_size[0] or h_ratio < 1.2*screen_size[2]) or (1.2*v_ratio > screen_size[1] or v_ratio < 1.2*screen_size[3]) and not gaze.is_blinking():
            print(bad_count)
            bad_count = 0
            window2.withdraw()
    else:
        bad_count = bad_count + 1

    #sleep(3)
    #canvas.delete(warning)
    window2.after(1000, main)

main()

window2.mainloop()