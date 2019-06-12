import tkinter as tk
import cv2
import PIL.Image, PIL.ImageTk
import sa1
import sql_eye as sql

m = 0
n = 0
print('import photo...')
pilImage = PIL.Image.open("IMG_3.jpg")
pilImage = pilImage.resize((1024, 720), PIL.Image.ANTIALIAS)

pilImage2 = PIL.Image.open("IMG_4.jpg")
pilImage2 = pilImage2.resize((1024, 720), PIL.Image.ANTIALIAS)

class MainWindow(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        window = self

        #self.canvas = tk.Canvas(window, width=self.vid.width, height=self.vid.height)
        self.canvas = tk.Canvas(window, width=1000, height=600)
        self.canvas.pack()

        # VIDEO
        print('loading camera...')
        self.vid = cv2.VideoCapture(1)
        print('initialization of the algorithm')
        self.button = tk.Button(window, text="Choose threshold", command=self.changeState)
        self.button.pack(side="top")

        self.btn_snapshot = tk.Button(window, text="Filed of the eyes", width=20, command=self.EyeRegState)
        self.btn_snapshot.pack(anchor=tk.CENTER, expand=True)

        self.Slider_1 = tk.Scale(window, length=300.0, from_=0, to=255,
                                      orient=tk.HORIZONTAL, )

        self.Slider_1.set(sql.getCalibr())
        self.Slider_1.pack()
        print('loading is done')
        self.show_frame()


    def show_frame(self):
        thrTurn = self.create_window(0)
        eyeReg = self.EyeReg(0)
        _, frame = self.vid.read()
        Threshold = self.Slider_1.get()

        sa1.mainfunc(frame, Threshold, thrTurn, eyeReg)
        coordinate = sql.getLast()
        #print(str(coordinate)+' coordinate')

        if coordinate > 1.0:
            self.photo1 = PIL.ImageTk.PhotoImage(pilImage)
            #print('1')
        else:
            self.photo1 = PIL.ImageTk.PhotoImage(pilImage2)
            #print('2')
        #canvas1 = tk.Canvas(self, width=1024, height=720)
        self.canvas.create_image(0, 0, image=self.photo1, anchor=tk.NW)
        self.canvas.pack()
        tk.Label(root).after(10, self.show_frame)

    def changeState(self):
        self.create_window(1)

    def create_window(self, state):
        global m
        if state == 0:
            state = m
        elif state == 1:
            cv2.destroyAllWindows()
            m = not m
            state = 1
        thrTurn = state
        return thrTurn

    def EyeRegState(self):
        self.EyeReg(1)

    def EyeReg(self, state):
        global n
        if state == 0:
            state = n
        elif state == 1:
            cv2.destroyAllWindows()
            n = not n
            state = 1
        eyeReg = state
        return eyeReg


def on_closing():
    sql.closeCursor()
    root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    main = MainWindow(root)
    main.pack(side="top", fill="both", expand=True)

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()



