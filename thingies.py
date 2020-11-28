import cv2
from gaze_tracking import GazeTracking
from tkinter import *
from time import sleep
from datetime import datetime

window1 = Tk()
window1.attributes('-fullscreen', True)
window1.update_idletasks()
w = window1.winfo_screenwidth()
h = window1.winfo_screenheight()
canvas =  Canvas(window1, bg='black', width=w, height=h)
canvas.pack()

warning = canvas.create_text(-1000, -1000, fill="White", text="You aren't looking in the middle")

coords = [(10, 10, 30, 30), (w-10, h-10, w-40, h-40) ]

circle = []

work_time = 30 # int(input("Enter the number of minutes you want to work for\n")) * 60
break_time = 30 # int(input("Enter the number of minutes you want to rest for\n")) * 60
start_time = datetime.now()

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
screen_size = []

display= canvas.create_text(w/2, h/2, fill="white", text="Press enter to start. Look at the blue ball.")

i = 0

def initialise_balls():
    global circle
    for i in range(2):
        circle.append(canvas.create_oval(-100,-100,-100,-100, outline='blue', fill='blue'))

def callabirate(event = None):
    canvas.coords(circle[i], coords[i])
    _, frame = webcam.read()
    gaze.refresh(frame)
    frame = gaze.annotated_frame()
    screen_size.append(gaze.horizontal_ratio())
    screen_size.append(gaze.vertical_ratio())
    window1.after(1000, success)


def deleteBall():
    canvas.move(circle[i], -10000, -10000)

def success():
    global i
    canvas.itemconfigure(display, text="Amazing! Press enter for the next ball please :)")
    deleteBall()
    if i == len(coords) - 1:
        print(i)
        canvas.itemconfigure(display, text="Finished! We will now start the application.")
        window1.destroy()
    i = i + 1

initialise_balls()
window1.bind("<Escape>", lambda e: e.widget.quit())
window1.bind("<Return>", callabirate)
window1.mainloop()

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

