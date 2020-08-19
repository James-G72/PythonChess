# Attempting to make a basic chess game whereby the computer randomly selects a next move.
# This will form the framework for a later project that looks to pit a manual algorithm against a neural network (probably NEAT)
# The original plan was to use matplotlib but for ease tkinter will be used instead as this makes adding controls very simple

import numpy as np
import pandas as pd
import base64
import tkinter as tk
import center_tk_window as ctw
import time
import math

# -----------------------  Section 1  -----------------------
# Defining the GameBoard class and all functionality required to interact with the board


class GameBoard(tk.Frame):
    def __init__(self, parent, size=80, rows=8, columns=8, color1="#ffffff", color2="#474747"):
        # Can be customised for different sizes but defaults to a classic chess board
        # The default colors here are pure white and dark gray

        # Adding all of the pictures from Pieces folder
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
        # This allows for the tracking of the square selected
        global selectedsquare
        selectedsquare = [0,0]

        # Assumed as square but can be other
        c_width = columns * size
        c_height = rows * size

        # Creating the canvas for the window
        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, width=c_width, height=c_height, background="bisque")
        self.canvas.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Adding a quit button
        self.quit_button = tk.Button(self,text="QUIT", fg="red", command=self.quit)
        self.quit_button.place(x=self.size*8 + 10, y=100, width=50, height=20)

        self.canvas.bind("<Button 1>",self.getcoords)


        # If a the user changes the window size then the refresh call is made. This is defined below
        self.canvas.bind("<Configure>", self.refresh)

    def getcoords(self, event):
        global x0,y0
        x0 = event.x
        y0 = event.y
        # This retrives the curreny x and y coordinates in terms of pixels from the top left
        # I am not sure if this is specific to mine but there is 76 pixels per square
        self.highlightsquare(x0,y0)

    def highlightsquare(self, xcoord, ycoord):
        offset = 77
        squarex = math.floor(xcoord/offset)
        squarey = math.floor(ycoord/offset)
        self.canvas.create_line(squarex*offset,squarey*offset,squarex*offset+offset,squarey*offset,fill='red',width=3)
        self.canvas.create_line(squarex*offset,squarey*offset,squarex*offset,squarey*offset+offset,fill='red',width=3)
        self.canvas.create_line(squarex*offset+offset,squarey*offset+offset,squarex*offset+offset,squarey*offset,fill='red',width=3)
        self.canvas.create_line(squarex*offset+offset,squarey*offset+offset,squarex*offset,squarey*offset+offset,fill='red',width=3)

    def addpiece(self, name, image, row=0, column=0):
        # We can add a piece to the board at the requested location
        # This hijacks the function below by creating the specified piece first
        self.canvas.create_image(0,0, image=image, tags=(name, "piece"), anchor="c")
        self.placepiece(name, row, column)

    def removepiece(self, name):
        # This is used not only for when a piece is removed from the board
        self.canvas.delete(name)
        del self.pieces[name] # We also remove it from the pieces list

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

# -----------------------  Section 2  -----------------------
# Initialising the board
playWindow = tk.Tk() # Root window is created
board = GameBoard(playWindow) # Initialising the game board within the root window
board.pack(side="top", fill="both", expand="true", padx=0, pady=0) # Packing and displaying
playWindow.resizable(width=False, height=False) # This is a very important line that stops the window being edited which makes the layout much easier
# Setting the geometry to include all of the buttons.
# I will need to find a better way of doing this
playWindow.geometry(str(board.size*8+100)+"x"+str(board.size*8))
ctw.center_on_screen(playWindow) # This is a nifty module that centers the window for us
board.defaults() # Setting the board for the start of a game

playWindow.mainloop() # Main loop is set here
