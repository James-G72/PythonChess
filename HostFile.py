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
    def __init__(self, parent, side_size, square_size=80, rows=8, columns=8, color1="#ffffff", color2="#474747"):
        # Can be customised for different sizes but defaults to a classic chess board
        # The default colors here are pure white and dark gray

        # Assembling
        self.rows = rows
        self.columns = columns
        self.size = square_size
        self.side_size = side_size
        self.color1 = color1
        self.color2 = color2
        self.pieces = {}
        self.piece_description = {}
        self.square_virtual_size = 77
        self.initiated = False # Has a game started
        self.piece_index = pd.read_pickle("/Users/jamesgower2/Loughborough University/TSteffenProjects - James/PythonChess/initial_board.pkl") # Tracks all the pieces on the board
        self.boardrow = 0 # This tracks what row we're on

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
        with open("Pieces/lock.gif","rb") as imageFile:
            string = base64.b64encode(imageFile.read())
        imageholder["lock"] = tk.PhotoImage(data=string)
        self.imageholder = imageholder

        # Adding text for piece descriptions
        self.piece_description["r"] = "Black Castle"
        self.piece_description["R"] = "White Castle"
        self.piece_description["b"] = "Black Bishop"
        self.piece_description["B"] = "White Bishop"
        self.piece_description["k"] = "Black King"
        self.piece_description["K"] = "White King"
        self.piece_description["n"] = "Black Knight"
        self.piece_description["N"] = "White Knight"
        self.piece_description["q"] = "Black Queen"
        self.piece_description["Q"] = "White Queen"
        self.piece_description["p"] = "Black Pawn"
        self.piece_description["P"] = "White Pawn"


        # Assumed as square but can be other
        c_width = columns * self.size
        c_height = rows * self.size

        # Creating the canvas for the window
        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, width=c_width, height=c_height, background="bisque")
        self.canvas.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Adding a quit button
        self.quit_button = tk.Button(self,text="QUIT", fg="red", command=self.quit)
        self.quit_button.place(x=self.square_virtual_size*8 + self.side_size/2, y=self.square_virtual_size*8-40, width=50, height=20)

        # Adding a square/piece selected tracker
        self.canvas.create_rectangle(self.square_virtual_size*8 + 4,2,self.square_virtual_size*8 + 10+192,90,width=2)
        self.selection_heading = tk.Label(self,text="Current Selection:",font=("TKDefaultFont",18),bg="bisque")
        self.selection_heading.place(x=self.square_virtual_size*8 + 30, y=18, height=16)
        self.square_text_x = tk.StringVar()
        self.square_text_x.set("Selected Square (x) = None")
        self.selected_displaysx = tk.Label(self,textvariable=self.square_text_x, bg="bisque")
        self.selected_displaysx.place(x=self.square_virtual_size*8 + 15, y=40, height=16)
        self.square_text_y = tk.StringVar()
        self.square_text_y.set("Selected Square (y) = None")
        self.selected_displaysy = tk.Label(self,textvariable=self.square_text_y, bg="bisque")
        self.selected_displaysy.place(x=self.square_virtual_size*8 + 15, y=60, height=16)
        self.square_text_displaypiece = tk.StringVar()
        self.square_text_displaypiece.set("Selected Piece = None")
        self.selected_displaypiece = tk.Label(self,textvariable=self.square_text_displaypiece, bg="bisque")
        self.selected_displaypiece.place(x=self.square_virtual_size*8 + 15, y=80, height=16)

        # Adding playmode selector
        self.canvas.create_rectangle(self.square_virtual_size*8 + 4,100,self.square_virtual_size*8 + 10+192,176,width=2)
        self.mode_heading = tk.Label(self,text="Playing Modes:",font=("TKDefaultFont",18),bg="bisque")
        self.mode_heading.place(x=self.square_virtual_size*8 + 45, y=115, height=20)
        self.player1_label = tk.Label(self,text="White:",bg="bisque")
        self.player1_label.place(x=self.square_virtual_size*8 + 15, y=145, height=16)
        self.player2_label = tk.Label(self,text="Black:",bg="bisque")
        self.player2_label.place(x=self.square_virtual_size*8 + 15, y=165, height=16)
        self.playmode1 = tk.StringVar()
        self.playmode1.set("Person")
        self.playmode2 = tk.StringVar()
        self.playmode2.set("Computer")
        self.player1 = tk.OptionMenu(self,self.playmode1,"Person","Computer")
        self.player1.place(x=self.square_virtual_size*8 + 80, y=145, height=16)
        self.player1.config(background="bisque") # For optionmenu the bg abbreviation means in the dropdown
        self.player2 = tk.OptionMenu(self,self.playmode2,"Person","Computer")
        self.player2.place(x=self.square_virtual_size * 8+80,y=165,height=16)
        self.player2.config(background="bisque") # For optionmenu the bg abbreviation means in the dropdown

        # Start and reset button
        self.reset_button = tk.Button(self,text="Reset Board",bg="black", command=self.defaults)
        self.reset_button.place(x=self.square_virtual_size*8 + 115, y=202, height=16)
        self.start_button = tk.Button(self,text="Start!",fg="green",background="black",font=("TKDefaultFont",30), command=self.initiate)
        self.start_button.place(x=self.square_virtual_size * 8+20,y=196,height=28)


        # Binding configuration and left mouse click
        self.canvas.bind("<Button 1>",self.getcoords) # This allows the clicking to be tracked
        # If a the user changes the window size then the refresh call is made. This is defined below
        self.canvas.bind("<Configure>", self.refresh)

    def getcoords(self, event):
        global x0,y0
        x0 = event.x
        y0 = event.y
        # This retrives the curreny x and y coordinates in terms of pixels from the top left
        # I am not sure if this is specific to mine but there is 77 pixels per square
        self.selectsquare(x0,y0)

    def selectsquare(self, xcoord, ycoord):
        self.canvas.delete("highlight")
        offset = self.square_virtual_size # This is the number required to make it work......
        squarex = math.floor(xcoord/offset)
        squarey = math.floor(ycoord/offset)
        if squarex <=7 and squarey <=7:
            self.highlightsquare(squarex,squarey,"red",'highlight')
            self.square_text_x.set("Selected Square (x) = "+str(squarex+1))
            self.square_text_y.set("Selected Square (y) = "+str(squarey+1))
            found_key = []
            for key,value in self.pieces.items():
                if (value == (squarex,squarey)):
                    found_key=key
            if found_key == []:
                occupier = "None"
            else:
                occupier = self.piece_description[found_key[0]]
            self.square_text_displaypiece.set("Selected Piece = "+occupier)

            if self.initiated and found_key != []: # If a game has been started
                self.visualisemoves(squarex,squarey,found_key)
        else:
            # If the click is off of the square
            self.square_text_x.set("Selected Square (x) = None")
            self.square_text_y.set("Selected Square (y) = None")
            self.square_text_displaypiece.set("Selected Piece = None")

    def highlightsquare(self,squarex,squarey,colour,tag):
        offset = self.square_virtual_size
        if colour == "green":
            colour = "#00cc00"
        self.canvas.create_line(squarex * offset,squarey * offset,squarex * offset+offset,squarey * offset,fill=colour,width=3,tag=tag)
        self.canvas.create_line(squarex * offset,squarey * offset,squarex * offset,squarey * offset+offset,fill=colour,width=3,tag=tag)
        self.canvas.create_line(squarex * offset+offset,squarey * offset+offset,squarex * offset+offset,squarey * offset,fill=colour,width=3,tag=tag)
        self.canvas.create_line(squarex * offset+offset,squarey * offset+offset,squarex * offset,squarey * offset+offset,fill=colour,width=3,tag=tag)

    def possiblemoves(self,squarex,squarey,piece_code):
        returnlist = []
        # Valid square calculations for the pawn which is the most irregular
        if piece_code[0] == "p" or piece_code[0] == "P":
            moves = self.piece_index.loc[:,piece_code]
            if moves[0] == moves[self.boardrow-1]: # Special case for the first time a pawn is moved
                doublemove = True
                factor = 2
            if piece_code[0] == "p":
                returnlist.append(str(squarex)+str(squarey+factor))
            else:
                returnlist.append(str(squarex)+str(squarey-factor))
            return returnlist
        elif piece_code[0] == "r" or piece_code[0] == "R":
            # Check all the possible directions
            return []
        else:
            return ["33",'44']

        # def checksquare(color,)

    def visualisemoves(self,squarex,squarey,piece_code):
        self.canvas.delete("example")
        offset = self.square_virtual_size # This is the number required to make it work......
        factor = 1 # This accouts for the double move on a pawns first turn
        target_squares = self.possiblemoves(squarex,squarey,piece_code)
        if piece_code[0] == "n" or piece_code[0] == "N":
            # Taking into account the the way a knight moves indirectly
            for plotter in target_squares:
                self.highlightsquare(int(plotter[0]),int(plotter[1]),"green","example")
        else:
            # All other pieces can be a straight line
            for plotter in target_squares:
                self.highlightsquare(int(plotter[0]),int(plotter[1]),"green","example")

    def addpiece(self, name, image, column=0, row=0):
        # We can add a piece to the board at the requested location
        # This hijacks the function below by creating the specified piece first
        self.canvas.create_image(0,0, image=image, tags=(name, "piece"), anchor="c")
        self.piece_index.loc[self.boardrow,name] = str(column)+str(row)
        self.placepiece(name, row, column)

    def removepiece(self, name):
        # This is used not only for when a piece is removed from the board
        self.canvas.delete(name)
        del self.pieces[name] # We also remove it from the pieces list

    def placepiece(self, name, column, row):
        '''Place a piece at the given row/column'''
        self.pieces[name] = (column,row)
        x0 = (column * self.size) + int(self.size/2)
        y0 = (row * self.size) + int(self.size/2)
        self.canvas.coords(name, x0, y0)

    def defaults(self):
        '''Sets the board up for a fresh game'''
        # First we clear the board if it isn't already empty
        keylist = list(self.pieces.keys())
        for x in keylist:
            self.removepiece(x)

        # Then we add in pieces 1 by 1
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

        self.player1.config(state="normal")  # Enabling the dropdown options
        self.player2.config(state="normal")  # Enabling the dropdown options
        self.canvas.delete("lock1") # Removing the lock symbol
        self.canvas.delete("lock2") # Removing the lock symbol
        self.initiated = False # Essentially saying that the game is no longer active

    def initiate(self):
        # Start the game here
        self.initiated = True # Indicates that the game has started
        print("Start")
        self.player1.config(state="disabled")  # Disabling the dropdown options
        self.player2.config(state="disabled")  # Disabling the dropdown options
        self.canvas.create_image(0,0, image=self.imageholder["lock"],tags="lock1", anchor="c")
        self.canvas.create_image(0,0,image=self.imageholder["lock"],tags="lock2",anchor="c")
        self.canvas.coords("lock1",775,140)
        self.canvas.coords("lock2",785,160)
        self.boardrow += 1

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

# Having done some research it is recommended to store the logic and information for moves in a pieces class
class ChessPiece():
    def __init__(self,piece_id):
        self.id = piece_id
        self.check = False
        self.moves = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7])

        # Now we set the default positions of the piece depending on what type it is at the start of the game
        if self.id == "p" or self.id == "P": # Then it is a pawn
            t = 1



# -----------------------  Section 2  -----------------------
# Initialising the board
playWindow = tk.Tk() # Root window is created
side_size = 200 # This affects the amount of space on the right of the board
board = GameBoard(playWindow,side_size=side_size) # Initialising the game board within the root window
board.pack(side="top", fill="both", expand="true", padx=0, pady=0) # Packing and displaying
playWindow.resizable(width=False, height=False) # This is a very important line that stops the window being edited which makes the layout much easier
# Setting the geometry to include all of the buttons.
# I will need to find a better way of doing this
playWindow.geometry(str(board.size*8+side_size)+"x"+str(board.size*8))
ctw.center_on_screen(playWindow) # This is a nifty module that centers the window for us
board.defaults() # Setting the board for the start of a game

playWindow.mainloop() # Main loop is set here
