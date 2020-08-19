# Attempting to make a basic chess game whereby the computer randomly selects a next move.
# This will form the framework for a later project that looks to pit a manual algorithm against a neural network (probably NEAT)
# The original plan was to use matplotlib but for ease tkinter will be used instead as this makes adding controls very simple

import numpy as np
import pandas as pd
import base64
import tkinter as tk
import center_tk_window as ctw

class GameBoard(tk.Frame):
    def __init__(self, parent, size=10, rows=8, columns=8, color1="#ffffff", color2="#474747"):
        # Can be customised for different sizes but defaults to a classic chess board
        # The default colors here are pure white and dark gray

        # Adding all of the pictures
        imageholder = {}
        piecelist = "bknpqr"
        colorlist = "bw"
        for f in piecelist:
            for l in colorlist:
                with open("Pieces/"+f+l+".gif","rb") as imageFile:
                    string = base64.b64encode(imageFile.read())
                if l == "w":
                    imageholder[f.capitalize()] = tk.PhotoImage(data=string)
                else:
                    imageholder[f] = tk.PhotoImage(data=string)
        self.imageholder = imageholder

        # Assembling
        self.rows = rows
        self.columns = columns
        self.size = size
        self.color1 = color1
        self.color2 = color2
        self.pieces = {}

        # Assumed as square but can be other
        c_width = columns * size
        c_height = rows * size

        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, width=c_width, height=c_height, background="bisque")
        self.canvas.pack(side="top", fill="both", expand=True, padx=2, pady=2)

        # If a the user changes the window size then the refresh call is made. This is defined below
        self.canvas.bind("<Configure>", self.refresh)

    def addpiece(self, name, image, row=0, column=0):
        # We can add a piece to the board at the requested location
        # This hijacks the function below by creating the specified piece first
        self.canvas.create_image(0,0, image=image, tags=(name, "piece"), anchor="c")
        self.placepiece(name, row, column)

    def placepiece(self, name, row, column):
        '''Place a piece at the given row/column'''
        self.pieces[name] = (row, column)
        x0 = (column * self.size) + int(self.size/2)
        y0 = (row * self.size) + int(self.size/2)
        self.canvas.coords(name, x0, y0)

    def defaults(self):
        '''Sets the board up for a fresh game'''
        # Castles
        self.addpiece("r1",self.imageholder["r"],0,0)
        self.addpiece("r2",self.imageholder["r"],0,7)
        self.addpiece("R1",self.imageholder["R"],7,0)
        self.addpiece("R2",self.imageholder["R"],7,7)
        # Naves
        self.addpiece("n1",self.imageholder["n"],0,1)
        self.addpiece("n2",self.imageholder["n"],0,6)
        self.addpiece("N1",self.imageholder["N"],7,1)
        self.addpiece("N2",self.imageholder["N"],7,6)
        # Bishops
        self.addpiece("b1",self.imageholder["b"],0,2)
        self.addpiece("b2",self.imageholder["b"],0,5)
        self.addpiece("B1",self.imageholder["B"],7,2)
        self.addpiece("B2",self.imageholder["B"],7,5)
        # Queens
        self.addpiece("q1",self.imageholder["q"],0,3)
        self.addpiece("Q1",self.imageholder["Q"],7,3)
        # Kings
        self.addpiece("k1",self.imageholder["k"],0,4)
        self.addpiece("K1",self.imageholder["K"],7,4)
        # Pawns - This can easily be looped
        for x in range(0,8):
            self.addpiece("p"+str(x+1),self.imageholder["p"],1,x)
            self.addpiece("P"+str(x+1),self.imageholder["P"],6,x)

    def refresh(self, event):
        '''Redraw the board, possibly in response to window being resized'''
        xsize = int((event.width-1) / self.columns)
        ysize = int((event.height-1) / self.rows)
        self.size = min(xsize, ysize)
        self.canvas.delete("square")
        color = self.color2
        for row in range(self.rows):
            color = self.color1 if color == self.color2 else self.color2
            for col in range(self.columns):
                x1 = (col * self.size)
                y1 = (row * self.size)
                x2 = x1 + self.size
                y2 = y1 + self.size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")
                color = self.color1 if color == self.color2 else self.color2
        for name in self.pieces:
            self.placepiece(name, self.pieces[name][0], self.pieces[name][1])
        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("square")

playWindow = tk.Tk() # Root window is called
board = GameBoard(playWindow,80) # Initialising the game board
board.pack(side="top", fill="both", expand="true", padx=4, pady=4) # Packing and displaying
board.defaults()
board.pack(side="top", fill="both", expand="true", padx=0, pady=0) # Packing and displaying
ctw.center_on_screen(playWindow) # This is a nifty module that centers the window for us
playWindow.mainloop() # Main loop is set here
