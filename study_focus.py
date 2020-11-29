import cv2
from gaze_tracking import GazeTracking
from tkinter import *
from time import sleep
from datetime import datetime, timedelta
from focus_callabirate import Callibrate
from platform import system
from subprocess import check_output
from pathlib import Path
import os
import pygame
import json
from configparser import ConfigParser

system_type = system()

config = ConfigParser()

with open('config.json', 'r') as f:
    config = json.load(f)

blacklist = config["blacklist"]


if system_type == "Windows":
    import wmi
    from subprocess import STARTUPINFO, STARTF_USESHOWWINDOW
    manager = wmi.WMI()
elif system_type == "Linux":
    import psutil
else:
    exit("Not a Usable Platform")


def get_processes():
    names = []
    if system_type == "Windows":
        for process in manager.Win32_Process():
            names.append(process.Name)
    elif system_type == "Linux":
        for process in psutil.process_iter():
            names.append(process.name().split("/")[0])
    names = list(set(names))
    return names


def get_programs():
    names = []
    if system_type == "Windows":
        links = list(Path("C:/ProgramData/Microsoft/Windows/Start Menu").rglob("*.lnk"))
        links += list(Path("C:/Users/" + os.getenv("USERNAME") + "/AppData/Roaming/Microsoft/Windows/Start Menu/Programs").rglob("*.lnk"))
        links = [str(link) for link in links]
        startupinfo = STARTUPINFO()
        startupinfo.dwFlags |= STARTF_USESHOWWINDOW
        for link in links:
            if not re.search(",", link) and not re.search("\(", link):
                double_slashed = link.replace("\\", "\\\\")
                cargs = ["wmic", "path", "win32_shortcutfile", "where", "name=\"{0}\"".format(double_slashed), "get", "target", "/value"]
                filename = list(filter(None, check_output(cargs, startupinfo=startupinfo).splitlines()))[0]
                print(filename)
                if filename != b"Target=":
                    names.append(filename.split(b"\\")[-1].decode("utf-8"))
    elif system_type == "Linux":
        for program in check_output(["/bin/bash", "-c", "compgen -c"]).splitlines():
            temp = program.decode('utf-8')
            if re.search("[a-zA-Z]", temp):
                names.append(temp)
    names = list(set(names))
    names.sort()
    return names


callabirator = Callibrate()
callabirator.calibrate()
screen_size = callabirator.get_screen_size()
callabirator.close_camera()

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)

root = Tk()
root.configure()
root.update_idletasks()

window2 = Toplevel(root)
window2.attributes('-fullscreen', True)
window2.update_idletasks()
w = window2.winfo_screenwidth()
h = window2.winfo_screenheight()


canvas2 =  Canvas(window2, bg='black', width=w, height=h)
canvas2.pack()
window2.withdraw()

success = canvas2.create_text(w/2, h/2, fill="White", text="YOU ARE NOT LOOKING AT THE SCREEN")

root.bind("<Escape>", lambda e: e.widget.quit())

bad_count = 0
bad_process = False


process_name = ""

FLASHTIME = 3
flash = False
flash_on = datetime.now()
flash_off = datetime.now()
checking = 1
processes = []

pygame.init()
pygame.mixer.init()

WORKTIME = 20
BREAKTIME = 5
current = ""
working = True

start_time = datetime.now()

canvas3 =  Canvas(root, bg='black', width=300, height=70)
canvas3.pack()

display_timer = canvas3.create_text(10, 5, fill="green", anchor=NW)

notification    =canvas3.create_text(10,35,fill="red", anchor=NW)


def timer():
    global current
    global working
    global start_time
    global timer
    global canvas3
    global root

    if working:
        current = str(start_time+timedelta(minutes=WORKTIME) - datetime.now())

    else:
        current = str(start_time+timedelta(minutes=BREAKTIME) -  datetime.now())

    current = current.split(".")[0]

    if current == "0:00:15":
        if working:
            canvas3.itemconfigure(notification, text="You need to take a break soon!")
        else:
            canvas3.itemconfigure(notification, text="You need to get back to work soon!")

    if current == "0:00:00" or "-" in current:
        window2.withdraw()
        working = not working
        start_time = datetime.now()
        canvas3.itemconfigure(notification, text="")
    canvas3.itemconfigure(display_timer, text=current)
    root.after(1000, timer)

def main():
    global flash
    global flash_on
    global flash_off
    global checking
    global blacklist
    global success
    global bad_count
    global bad_process
    global process_name
    global processes

    _, frame = webcam.read()
    gaze.refresh(frame)
    frame = gaze.annotated_frame()
    h_ratio = gaze.horizontal_ratio()
    v_ratio = gaze.vertical_ratio()

    if working:
        checking -= 1
        if not checking:
            checking = 5
            processes = get_processes()
        for item in blacklist:
            if item in processes:
                process_name = item
                bad_process = True
                break

        if bad_process and not flash:
            if (datetime.now() - flash_off).total_seconds() > 3.0:
                flash_on = datetime.now()
                flash = True


        if h_ratio and v_ratio:
            if (1.2*h_ratio < screen_size[0] or h_ratio > 1.2*screen_size[2]) or (1.2*v_ratio  < screen_size[1] or v_ratio > 1.2*screen_size[3]) and not gaze.is_blinking():
                bad_count = bad_count + 1
                if bad_count > 6:

                    window2.deiconify()
                    print("Print please")
                    print(bad_count)
                    canvas2.itemconfigure(success, text="YOU ARE NOT LOOKING AT THE SCREEN")
                    bark = pygame.mixer.Sound('bark.wav')
                    bark.play()


            elif (1.2*h_ratio > screen_size[0] or h_ratio < 1.2*screen_size[2]) or (1.2*v_ratio > screen_size[1] or v_ratio < 1.2*screen_size[3]) and not gaze.is_blinking():
                print(bad_count)
                bad_count = 0
                window2.withdraw()
        else:
            bad_count = bad_count + 1
            if bad_count > 6:
               window2.deiconify()
               canvas2.itemconfigure(success, text="YOU ARE NOT LOOKING AT THE SCREEN")

        if bad_process and flash:
            window2.deiconify()
            canvas2.itemconfigure(success, text="YOU ARE DOING SOMETHING NAUGHTY. CLOSE %s" % (process_name))
            #bark = pygame.mixer.Sound('bark.wav')
            #bark.play()
            if (datetime.now() - flash_on).total_seconds() > 3.0:
                window2.withdraw()
                flash = False
                flash_off = datetime.now()
                bad_process = False
    else:
        if h_ratio and v_ratio:
            if (1.2*h_ratio > screen_size[0] or h_ratio < 1.2*screen_size[2]) or (1.2*v_ratio  > screen_size[1] or v_ratio < 1.2*screen_size[3]) and not gaze.is_blinking():
                bad_count = bad_count + 1
                if bad_count > 6:

                    window2.deiconify()
                    print("Print please")
                    print(bad_count)
                    canvas2.itemconfigure(success, text="YOU ARE LOOKING AT THE SCREEN. TAKE A BREAK")
                    bark = pygame.mixer.Sound('bark.wav')
                    bark.play()


            elif (h_ratio < screen_size[0] or h_ratio > 1.2*screen_size[2]) or (1.2*v_ratio < screen_size[1] or v_ratio > 1.2*screen_size[3]) and not gaze.is_blinking():
                print(bad_count)
                bad_count = 0
                window2.withdraw()
        else:
            bad_count = bad_count + 1
            print(bad_count)
            if bad_count > 6:
                window2.deiconify()
                canvas2.itemconfigure(success, text="YOU ARE LOOKING AT THE SCREEN. TAKE A BREAK")


    root.after(500, main)

root.after(5,timer())
root.after(5,main())

root.mainloop()
