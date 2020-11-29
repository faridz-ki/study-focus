
import cv2
from gaze_tracking import GazeTracking
from tkinter import *

class Callibrate(object):
    def __init__(self):
        self.gaze = GazeTracking()
        self.webcam = cv2.VideoCapture(0)
        self.hori = []
        self.verti = []
        self.circle = []
        self.i = 0
        self.window1 = Tk()
        pass

    def close_camera(self):
        self.webcam.release()

    def get_screen_size(self):
        self.hori = list(filter(None, self.hori))
        self.verti = list(filter(None, self.verti))
        print(self.hori)
        print(self.verti)
        return [min(self.hori), min(self.verti), max(self.hori), max(self.verti)]


    def calibrate(self):
        self.window1.attributes('-fullscreen', True)
        self.window1.update_idletasks()
        self.w = self.window1.winfo_screenwidth()
        self.h = self.window1.winfo_screenheight()
        self.coords = [(10, 10, 30, 30),
            (self.w-10, self.h-10, self.w-30, self.h-30),
            (self.w/2+10, 10, self.w/2-10, 30),
            (self.w/2+10, self.h-10, self.w/2-10, self.h-30),
            (10, self.h-10, 30, self.h-30),
            (self.w-10, 10, self.w-30, 30),
            (10, self.h/2-10, 30, self.h/2+10),
            (self.w-10, self.h/2-10, self.w-30, self.h/2+10)]
        self.canvas = Canvas(self.window1, bg='black', width=self.w, height=self.h)
        self.canvas.pack()
        self.display = self.canvas.create_text(self.w/2, self.h/2, fill="white", text="Press enter to start. Look at the white ball.")
        self._initialise_balls()
        print(self.canvas.coords(self.circle[0]))
        self.window1.bind("<Escape>", lambda e: e.widget.quit())
        self.window1.bind("<Return>", self._callabirate)
        self.window1.mainloop()

    def _initialise_balls(self):
        for i in range(len(self.coords)):
            self.circle.append(self.canvas.create_oval(0, 0, 0, 0, outline='white', fill='white'))

    def _callabirate(self, event = None):
        self.canvas.coords(self.circle[self.i], self.coords[self.i])
        _, frame = self.webcam.read()
        self.gaze.refresh(frame)
        frame = self.gaze.annotated_frame()
        self.hori.append(self.gaze.horizontal_ratio())
        self.verti.append(self.gaze.vertical_ratio())
        self.window1.after(2000, self._success)

    def _deleteBall(self):
        self.canvas.move(self.circle[self.i], -10000, -10000)

    def _success(self):
        self.canvas.itemconfigure(self.display, text="Amazing! Press enter for the next ball please :)")
        self._deleteBall()
        if self.i == len(self.coords) - 1:
            self.canvas.itemconfigure(self.display, text="Finished! We will now start the application.")
            self.window1.after(1000, lambda: self.window1.destroy())
        self.i = self.i + 1
