import cv2
from gaze_tracking import GazeTracking
from tkinter import *
from time import sleep
from datetime import datetime
from focus_callabirate import Callibrate
from platform import system
from subprocess import check_output
from pathlib import Path

system_type = system()

blacklist = ["firefox.exe", "x-www-browser"]


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

    
    for item in blacklist:
        if item in get_processes():
            bad_process = True

    if h_ratio and v_ratio:
        if (1.1*h_ratio < screen_size[0] or h_ratio > 1.1*screen_size[2]) or (1.1*v_ratio  < screen_size[1] or v_ratio > 1.1*screen_size[3]) and not gaze.is_blinking():
            bad_count = bad_count + 1
            if bad_count > 10:
                window2.deiconify()
                print("Print please")
                print(bad_count)
                canvas2.itemconfigure(success, text="YOU ARE NOT LOOKING AT THE SCREEN")
            elif bad_process:
                window2.deiconify()
                canvas2.itemconfigure(success, text="YOU ARE DOING SOMETHING NAUGHTY")
        elif (1.1*h_ratio > screen_size[0] or h_ratio < 1.1*screen_size[2]) or (1.1*v_ratio > screen_size[1] or v_ratio < 1.1*screen_size[3]) and not gaze.is_blinking():
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