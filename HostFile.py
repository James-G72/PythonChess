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
# Importing the custom chess piece classes
import ChessPieces

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
        self.boardarray_pieces = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7])
        self.colourarray = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7])

        self.desiredsquare = [] # This is the square that the player wants to move
        self.squarechosen = False
        self.validclick = False
        self.movesquare = []

        # Adding all of the pictures from Images folder
        imageholder = {}
        piecelist = "bknpqr"
        colorlist = "bw"
        for f in piecelist:
            for l in colorlist:
                with open("Images/"+f+l+".gif","rb") as imageFile:
                    string = base64.b64encode(imageFile.read())
                if l == "w":
                    imageholder[f.capitalize()] = tk.PhotoImage(data=string)
                else:
                    imageholder[f] = tk.PhotoImage(data=string)
        with open("Images/lock.gif","rb") as imageFile:
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

        # Adding controls section to allow the game to be played
        self.canvas.create_rectangle(self.square_virtual_size*8 + 4,240,self.square_virtual_size*8 + 10+192,400,width=2)
        self.controls_heading = tk.Label(self,text="Controls:",font=("TKDefaultFont",18),bg="bisque")
        self.controls_heading.place(x=self.square_virtual_size*8 + 70, y=255, height=16)
        self.selectbuttonstring = tk.StringVar()
        self.selectbuttonstring.set("Select Piece")
        self.select_button = tk.Button(self,textvariable=self.selectbuttonstring,fg="black",background="black",font=("TKDefaultFont",12), command=self.lockselection)
        self.select_button.place(x=self.square_virtual_size * 8+20,y=285,height=20)
        self.square_text_displaypiece_bybutton = tk.StringVar()
        self.square_text_displaypiece_bybutton.set("None")
        self.selected_displaypiece_bybutton = tk.Label(self,textvariable=self.square_text_displaypiece_bybutton,bg="bisque")
        self.selected_displaypiece_bybutton.place(x=self.square_virtual_size * 8+118,y=285,height=16)
        self.canvas.create_rectangle(self.square_virtual_size * 8+16,298,self.square_virtual_size * 8+10+180,368,width=1)
        self.summary_heading = tk.Label(self,text="Summary:",font=("TKDefaultFont",10),bg="bisque")
        self.summary_heading.place(x=self.square_virtual_size*8 + 80, y=310, height=16)
        self.summarylabel1 = tk.Label(self,text="Move:",font=("TKDefaultFont",10),bg="bisque")
        self.summarylabel1.place(x=self.square_virtual_size * 8+50,y=324,height=16)
        self.summarylabel1_piece = tk.Label(self,textvariable=self.square_text_displaypiece_bybutton,font=("TKDefaultFont",10),bg="bisque")
        self.summarylabel1_piece.place(x=self.square_virtual_size * 8+120,y=324,height=16)
        self.summarylabel2 = tk.Label(self,text="From:",font=("TKDefaultFont",10),bg="bisque")
        self.summarylabel2.place(x=self.square_virtual_size * 8+50,y=338,height=16)
        self.oldsquare = tk.StringVar()
        self.oldsquare.set("[ , ]")
        self.summarylabel2_piece = tk.Label(self,textvariable=self.oldsquare,font=("TKDefaultFont",10),bg="bisque")
        self.summarylabel2_piece.place(x=self.square_virtual_size * 8+120,y=338,height=16)
        self.summarylabel3 = tk.Label(self,text="To:",font=("TKDefaultFont",10),bg="bisque")
        self.summarylabel3.place(x=self.square_virtual_size * 8+50,y=352,height=16)
        self.newsquare = tk.StringVar()
        self.newsquare.set("[ , ]")
        self.summarylabel3_piece = tk.Label(self,textvariable=self.newsquare,font=("TKDefaultFont",10),bg="bisque")
        self.summarylabel3_piece.place(x=self.square_virtual_size * 8+120,y=352,height=16)
        self.summarylabel1.place_forget()
        self.summarylabel1_piece.place_forget()
        self.summarylabel2.place_forget()
        self.summarylabel2_piece.place_forget()
        self.summarylabel3.place_forget()
        self.summarylabel3_piece.place_forget()

        self.movebutton = tk.Button(self,text="Move Piece",fg="black",background="black",font=("TKDefaultFont",22), command=self.movepiece)
        self.movebutton.place(x=self.square_virtual_size * 8+50,y=384,height=20)
        self.movebutton.config(state="disabled")

        # Binding configuration and left mouse click
        self.canvas.bind("<Button 1>",self.getcoords) # This allows the clicking to be tracked
        # If a the user changes the window size then the refresh call is made. This is defined below
        self.canvas.bind("<Configure>", self.refresh)

    def getcoords(self, event):
        global x0,y0
        x0 = event.x
        y0 = event.y
        # This retrieves the current x and y coordinates in terms of pixels from the top left
        # I am not sure if this is specific to mine but there is 77 pixels per square
        if self.initiated:
            self.selectsquare(x0,y0)

    def selectsquare(self, xcoords, ycoords):
        if self.squarechosen == False:
            offset = self.square_virtual_size # This is the number required to make it work......
            col = math.floor(xcoords/offset)
            row = math.floor(ycoords/offset)
            if col <= 7 and row <= 7:
                self.canvas.delete("move")
                self.canvas.delete("highlight")
                self.canvas.delete("example")
                self.highlightsquare(row,col,"blue",'highlight')
                self.square_text_x.set("Selected Square (x) = "+str(col+1))
                self.square_text_y.set("Selected Square (y) = "+str(row+1))
                found_key = []
                if self.boardarray_pieces.loc[row,col] != 0:
                    found_key = self.boardarray_pieces.loc[row,col].getid()
                if found_key == []:
                    occupier = "None"
                    self.validclick = False
                else:
                    occupier = self.piece_description[found_key[0]]
                    self.validclick = True
                self.desiredsquare = [row,col]
                self.square_text_displaypiece.set("Selected Piece = "+occupier)
                self.square_text_displaypiece_bybutton.set(occupier)

                if self.initiated and found_key != []: # If a game has been started
                    self.visualisemoves(row,col,found_key)
            else:
                # If the click is off of the square
                self.square_text_x.set("Selected Square (x) = None")
                self.square_text_y.set("Selected Square (y) = None")
                self.square_text_displaypiece.set("Selected Piece = None")
        else:
            # If the square has been locked
            offset = self.square_virtual_size # This is the number required to make it work......
            col = math.floor(xcoords/offset)
            row = math.floor(ycoords/offset)
            target_squares = self.possiblemoves(self.desiredsquare[0],self.desiredsquare[1])
            for plotter in target_squares:
                if plotter[0] == str(row) and plotter [1] == str(col):
                    self.canvas.delete("move")
                    self.highlightsquare(row,col,"green",'move')
                    self.movesquare = [row,col]
                    self.summarylabel3.place(x=self.square_virtual_size * 8+50,y=352,height=16)
                    self.summarylabel3_piece.place(x=self.square_virtual_size * 8+120,y=352,height=16)
                    self.newsquare.set("[ "+str(self.movesquare[0]+1)+" , "+str(self.movesquare[1]+1)+" ]")
                    self.movebutton.config(state="normal")

    def highlightsquare(self,row,col,colour,tag):
        offset = self.square_virtual_size
        if colour == "green":
            colour = "#00cc00" # This is just a lighter green than the standard "green" color to make it clearer on the board
        self.canvas.create_line(col * offset,row * offset,col * offset+offset,row * offset,fill=colour,width=3,tag=tag)
        self.canvas.create_line(col * offset,row * offset,col * offset,row * offset+offset,fill=colour,width=3,tag=tag)
        self.canvas.create_line(col * offset+offset,row * offset+offset,col * offset+offset,row * offset,fill=colour,width=3,tag=tag)
        self.canvas.create_line(col * offset+offset,row * offset+offset,col * offset,row * offset+offset,fill=colour,width=3,tag=tag)

    def visualisemoves(self,row,col,piece_code):
        self.canvas.delete("example")
        offset = self.square_virtual_size # This is the number required to make it work......
        factor = 1 # This accounts for the double move on a pawns first turn
        target_squares = self.possiblemoves(row,col)
        for plotter in target_squares:
            self.highlightsquare(int(plotter[0]),int(plotter[1]),"orange","example")

    def possiblemoves(self,row,col):
        squares = self.boardarray_pieces.loc[row,col].validsquares()
        return squares

    def addpiece(self, name, image, row, column):
        # We can add a piece to the board at the requested location
        # This hijacks the function below by creating the specified piece first
        self.canvas.create_image(0,0, image=image, tags=(name, "piece"), anchor="c")
        self.placepiece(name, row, column)

    def removepiece(self, name):
        # This is used not only for when a piece is removed from the board
        self.canvas.delete(name)
        del self.pieces[name] # We also remove it from the pieces list

    def placepiece(self, name, row, col):
        '''Place a piece at the given row/column'''
        self.pieces[name] = (row,col)
        x0 = (col * self.size) + int(self.size/2)
        y0 = (row * self.size) + int(self.size/2)
        self.canvas.coords(name, x0, y0)

    def defaults(self):
        '''Sets the board up for a fresh game'''
        self.start_button.config(state="normal")

        # Adding in pieces 1 by 1 and create the objects to store in boardarray
        # Castles
        r1 = ChessPieces.Rook("r1",0,0)
        r2 = ChessPieces.Rook("r2",0,7)
        R1 = ChessPieces.Rook("R1",7,0)
        R2 = ChessPieces.Rook("R2",7,7)
        self.addpiece("r1",self.imageholder["r"],0,0)
        self.boardarray_pieces.loc[0,0] = r1
        self.addpiece("r2",self.imageholder["r"],0,7)
        self.boardarray_pieces.loc[0,7] = r2
        self.addpiece("R1",self.imageholder["R"],7,0)
        self.boardarray_pieces.loc[7,0] = R1
        self.addpiece("R2",self.imageholder["R"],7,7)
        self.boardarray_pieces.loc[7,7] = R2
        # Naves
        n1 = ChessPieces.Knight("n1",0,1)
        n2 = ChessPieces.Knight("n2",0,6)
        N1 = ChessPieces.Knight("N1",7,1)
        N2 = ChessPieces.Knight("N2",7,6)
        self.addpiece("n1",self.imageholder["n"],0,1)
        self.boardarray_pieces.loc[0,1] = n1
        self.addpiece("n2",self.imageholder["n"],0,6)
        self.boardarray_pieces.loc[0,6] = n2
        self.addpiece("N1",self.imageholder["N"],7,1)
        self.boardarray_pieces.loc[7,1] = N1
        self.addpiece("N2",self.imageholder["N"],7,6)
        self.boardarray_pieces.loc[7,6] = N2
        # Bishops
        b1 = ChessPieces.Bishop("b1",0,2)
        b2 = ChessPieces.Bishop("b2",0,5)
        B1 = ChessPieces.Bishop("B1",7,2)
        B2 = ChessPieces.Bishop("B2",7,5)
        self.addpiece("b1",self.imageholder["b"],0,2)
        self.boardarray_pieces.loc[0,2] = b1
        self.addpiece("b2",self.imageholder["b"],0,5)
        self.boardarray_pieces.loc[0,5] = b2
        self.addpiece("B1",self.imageholder["B"],7,2)
        self.boardarray_pieces.loc[7,2] = B1
        self.addpiece("B2",self.imageholder["B"],7,5)
        self.boardarray_pieces.loc[7,5] = B2
        # Queens
        q1 = ChessPieces.Queen("q1",0,3)
        Q1 = ChessPieces.Queen("Q1",7,3)
        self.addpiece("q1",self.imageholder["q"],0,3)
        self.boardarray_pieces.loc[0,3] = q1
        self.addpiece("Q1",self.imageholder["Q"],7,3)
        self.boardarray_pieces.loc[7,3] = Q1
        # Kings
        k1 = ChessPieces.King("k1",0,4)
        K1 = ChessPieces.King("K1",7,4)
        self.addpiece("k1",self.imageholder["k"],0,4)
        self.boardarray_pieces.loc[0,4] = k1
        self.addpiece("K1",self.imageholder["K"],7,4)
        self.boardarray_pieces.loc[7,4] = K1
        # Pawns
        p1 = ChessPieces.Pawn("p1",1,0)
        p2 = ChessPieces.Pawn("p2",1,1)
        p3 = ChessPieces.Pawn("p3",1,2)
        p4 = ChessPieces.Pawn("p4",1,3)
        p5 = ChessPieces.Pawn("p5",1,4)
        p6 = ChessPieces.Pawn("p6",1,5)
        p7 = ChessPieces.Pawn("p7",1,6)
        p8 = ChessPieces.Pawn("p8",1,7)
        P1 = ChessPieces.Pawn("P1",6,0)
        P2 = ChessPieces.Pawn("P2",6,1)
        P3 = ChessPieces.Pawn("P3",6,2)
        P4 = ChessPieces.Pawn("P4",6,3)
        P5 = ChessPieces.Pawn("P5",6,4)
        P6 = ChessPieces.Pawn("P6",6,5)
        P7 = ChessPieces.Pawn("P7",6,6)
        P8 = ChessPieces.Pawn("P8",6,7)
        for x in range(0,8):
            self.addpiece("p"+str(x+1),self.imageholder["p"],1,x)
            self.addpiece("P"+str(x+1),self.imageholder["P"],6,x)
        self.boardarray_pieces.loc[1,0] = p1
        self.boardarray_pieces.loc[1,1] = p2
        self.boardarray_pieces.loc[1,2] = p3
        self.boardarray_pieces.loc[1,3] = p4
        self.boardarray_pieces.loc[1,4] = p5
        self.boardarray_pieces.loc[1,5] = p6
        self.boardarray_pieces.loc[1,6] = p7
        self.boardarray_pieces.loc[1,7] = p8
        self.boardarray_pieces.loc[6,0] = P1
        self.boardarray_pieces.loc[6,1] = P2
        self.boardarray_pieces.loc[6,2] = P3
        self.boardarray_pieces.loc[6,3] = P4
        self.boardarray_pieces.loc[6,4] = P5
        self.boardarray_pieces.loc[6,5] = P6
        self.boardarray_pieces.loc[6,6] = P7
        self.boardarray_pieces.loc[6,7] = P8

        # Updating the colourarray position
        self.colourarray = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7])
        self.colourarray.loc[0:1,:] = "b"
        self.colourarray.loc[6:7,:] = "w"

        self.player1.config(state="normal")  # Enabling the drop-down options
        self.player2.config(state="normal")
        self.canvas.delete("lock1") # Removing the lock symbol if its there
        self.canvas.delete("lock2")
        self.initiated = False # Essentially saying that the game is no longer active

    def initiate(self):
        # Start the game here
        self.initiated = True # Indicates that the game has started
        self.start_button.config(state="disabled")
        print("Start")
        self.player1.config(state="disabled")  # Disabling the drop-down options
        self.player2.config(state="disabled")
        self.canvas.create_image(0,0, image=self.imageholder["lock"],tags="lock1", anchor="c") # Adding lock image
        self.canvas.create_image(0,0,image=self.imageholder["lock"],tags="lock2",anchor="c")
        self.canvas.coords("lock1",785,140)
        self.canvas.coords("lock2",785,160)

    def lockselection(self):
        if self.validclick and self.squarechosen == False:
            self.squarechosen = True
            self.selectbuttonstring.set("Deselect Piece")
            self.selected_displaypiece_bybutton.config(background="green")
            self.summarylabel1.place(x=self.square_virtual_size * 8+50,y=324,height=16)
            self.oldsquare.set("[ "+str(self.desiredsquare[0]+1)+" , "+str(self.desiredsquare[1]+1)+" ]")
            self.summarylabel1_piece.place(x=self.square_virtual_size * 8+120,y=324,height=16)
            self.summarylabel2.place(x=self.square_virtual_size * 8+50,y=338,height=16)
            self.summarylabel2_piece.place(x=self.square_virtual_size * 8+120,y=338,height=16)
        elif self.squarechosen:
            self.selectbuttonstring.set("Select Piece")
            self.selected_displaypiece_bybutton.config(background="bisque")
            self.oldsquare.set("")
            self.newsquare.set("")
            self.movebutton.config(state="disabled")
            self.squarechosen = False
        else:
            return

    def movepiece(self):
        self.placepiece(self.boardarray_pieces.loc[self.desiredsquare[0],self.desiredsquare[1]].getid(),self.movesquare[0],self.movesquare[1])
        self.boardarray_pieces.loc[self.movesquare[0],self.movesquare[1]] = self.boardarray_pieces.loc[self.desiredsquare[0],self.desiredsquare[1]]
        self.boardarray_pieces.loc[self.desiredsquare[0],self.desiredsquare[1]] = 0
        self.colourarray.loc[self.desiredsquare[0],self.desiredsquare[1]] = 0
        self.colourarray.loc[self.movesquare[0],self.movesquare[1]] = self.boardarray_pieces.loc[self.movesquare[0],self.movesquare[1]].getcolour()
        self.boardarray_pieces.loc[self.movesquare[0],self.movesquare[1]].iterate()
        self.lockselection()
        self.canvas.delete("highlight")
        self.canvas.delete("example")
        self.canvas.delete("move")
        # Allows for the the piece valid spaces to be updated by the latest move
        self.update_piecemoves()

    def update_piecemoves(self):
        # Later on it would be good to add some optimisation here but for now it is enough to cycle though
        for row in range(0,8):
            for col in range(0,8):
                if self.boardarray_pieces.loc[row,col] != 0: # If the space is blank we ship it
                    # Otherwise we call the update function in each of the pieces
                    self.boardarray_pieces.loc[row,col].updatemoves(row,col,self.boardarray_pieces,self.colourarray)

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
