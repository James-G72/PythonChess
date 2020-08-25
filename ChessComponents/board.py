import tkinter as tk
import pandas as pd
import numpy as np
import base64
import ChessComponents
import math

class GameBoard(tk.Frame):
    def __init__(self, parent, side_size, square_size=80, rows=8, columns=8, color1="#ffffff", color2="#474747"):
        # There is no need to edit any of the sizes. The default for side_size is 200
        # The default colors here are pure white and a dark gray

        # ---------------- Section 1 : Assembling basic variables ----------------
        self.rows = rows # 8
        self.columns = columns # 8
        self.size = square_size # This is the size in pixels of each square. This is essentially limited by the size of the chess piece images which are 60x60
        # In my experience the actual size of the squares isn't 80 when drawn. This is likely an overlap issue but comes out at 77
        self.square_virtual_size = 77 # So a variable is created to allow this to be carried throughout placement calculations

        self.side_size = side_size # The amount of blank space to the right of the board
        self.color1 = color1 # Colour 1 is the colour in the top left of the board
        self.color2 = color2 # Colour 2 is the colour in the top right of the board and cannot be pure black or the black pieces can't be seen
        self.pieces = {} # This is a dictionary that holds information about the pieces
        self.piece_description = {} # A dictionary used to relate the piece codes to readable descriptions for the user
        self.initiated = False # Has a game started and effects the interpretation of clicks on the canvas

        # All of the piece objects are held within a pandas DataFrame in their relative locations.
        # This variable ultimately describes the state of the game
        self.boardarray_pieces = pd.DataFrame(np.zeros((self.rows,self.columns)),index=range(0,self.rows),columns=range(0,self.columns))
        # The boardarray variable is accompanied by a colourarray which contains only the colour information
        # This is done to make referencing simpler when calculating moves.
        # I am not sure how necessary this is but should be quicker ad eventually might be changed to enums to avoid string comparisons
        self.colourarray = pd.DataFrame(np.zeros((self.rows,self.columns)),index=range(0,self.rows),columns=range(0,self.columns))
        self.current_turn_disp = tk.StringVar() # Displays the piece group which is current goinng
        self.current_turn_disp.set("") # Blank label won't display anything at first
        self.current_turn_check = "w" # This regulates which pieces can be moved. White goes first

        self.desiredsquare = [] # This is the square that the player wants to move and is locked using the select piece button
        self.squarechosen = False # This is triggered when a square is chosen
        self.validclick = False # This allows the board to know if a valid square to move to has been selected or not. This is stored on this level as it effects labels
        self.movesquare = [] # This is the square that the player wants to move to

        # Adding all of the pictures from Images folder
        self.imageholder = {} # Creating a dictionary
        piecelist = "bknpqr" # These are all the different types of pieces possible
        colorlist = "bw" # The two colours
        for f in piecelist: # Cycling through the pieces
            for l in colorlist: # Alternating between the two colours
                with open("Images/"+f+l+".gif","rb") as imageFile: # Opening the photo within the variable space
                    # The images can't be stored as P or p in MacOS as theyre read the same
                    # So the colour is introduced by adding b or w after the piece notation
                    string = base64.b64encode(imageFile.read()) # Creating a string that describes the gif in base64 format
                if l == "w": # Checking if this is a white piece
                    # When adding the image to a dictionary we use proper notation and capitalise the letter if it is a white piece
                    self.imageholder[f.capitalize()] = tk.PhotoImage(data=string)
                else:
                    # if it is a black piece then no change is required
                    self.imageholder[f] = tk.PhotoImage(data=string)
        # An additional image is a picture of a padlock to show that variables are locked
        with open("Images/lock.gif","rb") as imageFile:
            string = base64.b64encode(imageFile.read())
        self.imageholder["lock"] = tk.PhotoImage(data=string) # The picture is simply called lock in the dictionary

        # Adding text for piece descriptions to a dictionary which is then displayed to the user via a label
        # This helps to explain the notation going on above and is designed to be compatible with FEN
        # https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation
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

        # ---------------- Section 2 : Creating the board ----------------
        # The whole board is drawn within the window in TkInter
        # This a very long section defining a lot of stationary visuals for the GUI
        # Most of the placement is just done by eye to make sure it all looks okay

        c_width = columns * self.size # Width the canvas needs to be
        c_height = rows * self.size # Height the canvas needs to be

        # Creating the canvas for the window
        tk.Frame.__init__(self, parent)
        # This is self explanatory and provides a blank space upon which visual objects can be placed
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, width=c_width, height=c_height, background="bisque")
        self.canvas.pack(side="top", fill="both", expand=True, padx=10, pady=10) # Packed with a small amount of padding either side

        # Adding a quit button to allow the window to be terminated. This has the same effect as clicking the cross
        self.quit_button = tk.Button(self,text="Quit Game", fg="red", command=self.quit)
        self.quit_button.place(x=self.square_virtual_size*8 + self.side_size/2-20, y=self.square_virtual_size*8-40, height=20)

        # Adding a square/piece selected tracker
        self.canvas.create_rectangle(self.square_virtual_size*8 + 4,2,self.square_virtual_size*8 + 10+192,90,width=2) # Just a hollow rectangle to denote an area
        self.selection_heading = tk.Label(self,text="Current Selection:",font=("TKDefaultFont",18),bg="bisque") # Heading
        self.selection_heading.place(x=self.square_virtual_size*8 + 30, y=18, height=16)
        self.square_text_x = tk.StringVar() # StringVar variables can be dynamically changed
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
        self.playmode_height = 100 # Allows the whole rectangle to be moved up and down with contents
        self.canvas.create_rectangle(self.square_virtual_size*8 + 4,self.playmode_height,self.square_virtual_size*8 + 10+192,self.playmode_height+76,width=2)
        self.mode_heading = tk.Label(self,text="Playing Modes:",font=("TKDefaultFont",18),bg="bisque")
        self.mode_heading.place(x=self.square_virtual_size*8 + 45, y=self.playmode_height+15, height=20)
        self.player1_label = tk.Label(self,text="White:",bg="bisque")
        self.player1_label.place(x=self.square_virtual_size*8 + 15, y=self.playmode_height+45, height=16)
        self.player2_label = tk.Label(self,text="Black:",bg="bisque")
        self.player2_label.place(x=self.square_virtual_size*8 + 15, y=self.playmode_height+65, height=16)
        self.playmode1 = tk.StringVar()
        self.playmode1.set("Person")
        self.playmode2 = tk.StringVar()
        self.playmode2.set("Computer")
        self.player1 = tk.OptionMenu(self,self.playmode1,"Person","Computer")
        self.player1.place(x=self.square_virtual_size*8 + 80, y=self.playmode_height+45, height=16)
        self.player1.config(background="bisque") # For optionmenu the bg abbreviation means in the dropdown
        self.player2 = tk.OptionMenu(self,self.playmode2,"Person","Computer")
        self.player2.place(x=self.square_virtual_size * 8+80,y=self.playmode_height+65,height=16)
        self.player2.config(background="bisque") # For optionmenu the bg abbreviation means in the dropdown

        # Start and reset button
        self.reset_button = tk.Button(self,text="Reset Board",bg="black", command=self.defaults)
        self.reset_button.place(x=self.square_virtual_size*8 + 115, y=202, height=16)
        self.start_button = tk.Button(self,text="Start!",fg="green",background="black",font=("TKDefaultFont",30), command=self.initiate)
        self.start_button.place(x=self.square_virtual_size * 8+20,y=196,height=28)

        # Adding controls section to allow the game to be played
        self.controls_height = 225
        self.canvas.create_rectangle(self.square_virtual_size*8 + 4,self.controls_height,self.square_virtual_size*8 + 10+192,self.controls_height+160,width=2)
        self.controls_heading = tk.Label(self,text="Controls:",font=("TKDefaultFont",18),bg="bisque")
        self.controls_heading.place(x=self.square_virtual_size*8 + 70, y=self.controls_height+15, height=16)
        self.selectbuttonstring = tk.StringVar()
        self.selectbuttonstring.set("Select Piece")
        self.select_button = tk.Button(self,textvariable=self.selectbuttonstring,fg="black",background="black",font=("TKDefaultFont",12), command=self.lockselection)
        self.select_button.place(x=self.square_virtual_size * 8+20,y=self.controls_height+45,height=20)
        self.square_text_displaypiece_bybutton = tk.StringVar()
        self.square_text_displaypiece_bybutton.set("None")
        self.selected_displaypiece_bybutton = tk.Label(self,textvariable=self.square_text_displaypiece_bybutton,bg="bisque")
        self.selected_displaypiece_bybutton.place(x=self.square_virtual_size * 8+118,y=self.controls_height+45,height=16)
        self.canvas.create_rectangle(self.square_virtual_size * 8+16,self.controls_height+58,self.square_virtual_size * 8+10+180,self.controls_height+128,width=1)
        self.summary_heading = tk.Label(self,text="Summary:",font=("TKDefaultFont",10),bg="bisque")
        self.summary_heading.place(x=self.square_virtual_size*8 + 80, y=self.controls_height+70, height=16)
        self.summarylabel1 = tk.Label(self,text="Move:",font=("TKDefaultFont",10),bg="bisque")
        self.summarylabel1.place(x=self.square_virtual_size * 8+50,y=self.controls_height+84,height=16)
        self.summarylabel1_piece = tk.Label(self,textvariable=self.square_text_displaypiece_bybutton,font=("TKDefaultFont",10),bg="bisque")
        self.summarylabel1_piece.place(x=self.square_virtual_size * 8+120,y=self.controls_height+84,height=16)
        self.summarylabel2 = tk.Label(self,text="From:",font=("TKDefaultFont",10),bg="bisque")
        self.summarylabel2.place(x=self.square_virtual_size * 8+50,y=self.controls_height+98,height=16)
        self.oldsquare = tk.StringVar()
        self.oldsquare.set("[ , ]")
        self.summarylabel2_piece = tk.Label(self,textvariable=self.oldsquare,font=("TKDefaultFont",10),bg="bisque")
        self.summarylabel2_piece.place(x=self.square_virtual_size * 8+120,y=self.controls_height+98,height=16)
        self.summarylabel3 = tk.Label(self,text="To:",font=("TKDefaultFont",10),bg="bisque")
        self.summarylabel3.place(x=self.square_virtual_size * 8+50,y=self.controls_height+112,height=16)
        self.newsquare = tk.StringVar()
        self.newsquare.set("[ , ]")
        self.summarylabel3_piece = tk.Label(self,textvariable=self.newsquare,font=("TKDefaultFont",10),bg="bisque")
        self.summarylabel3_piece.place(x=self.square_virtual_size * 8+120,y=self.controls_height+112,height=16)

        self.movebutton = tk.Button(self,text="Move Piece",fg="black",background="black",font=("TKDefaultFont",22), command=self.movepiece)
        self.movebutton.place(x=self.square_virtual_size * 8+50,y=self.controls_height+144,height=20)
        self.movebutton.config(state="disabled")

        # Current turn indicator
        self.current_turn_indicator = tk.Label(self,text="Current Turn:",font=("TKDefaultFont",12),bg="bisque")
        self.current_turn_indicator.place(x=self.square_virtual_size * 8+60,y=400,height=20)
        self.current_turn_text = tk.Label(self,textvariable=self.current_turn_disp,font=("TKDefaultFont",16),bg="bisque")
        self.current_turn_text.place(x=self.square_virtual_size * 8+52,y=422,height=20)

        # Binding configuration and left mouse click
        self.canvas.bind("<Button 1>",self.getcoords) # This allows the clicking to be tracked
        # If a the user changes the window size then the refresh call is made. This is defined below
        self.canvas.bind("<Configure>", self.refresh) # This shouldn't happen as the size has been locked

    def getcoords(self, event):
        global x0,y0
        x0 = event.x # Event is a click
        y0 = event.y
        # This retrieves the current x and y coordinates in terms of pixels from the top left
        if self.initiated: # If the game is started....
            self.selectsquare(x0,y0) # This information is passed into the selectsquare method

    def selectsquare(self, xcoords, ycoords):
        valid = False # Allows the alternating turns of the two players to be observed
        offset = self.square_virtual_size  # This is the number required to make it work......
        col = math.floor(xcoords / offset) # Finding the square the player means
        row = math.floor(ycoords / offset)
        if self.squarechosen == False: # If we haven't chosen one yet then choose one
            if col <= 7 and row <= 7: # Have we clicked within the bounds of the board
                if self.current_turn_check == "w" and self.colourarray.loc[row,col] != "b": # Checking if it is the right colour
                    valid = True # Allowing access to additional code
                elif self.current_turn_check == "b" and self.colourarray.loc[row,col] != "w":
                    valid = True
                if valid:
                    self.canvas.delete("move") # Clearing all types of highlighting currently o the board
                    self.canvas.delete("highlight")
                    self.canvas.delete("example")
                    self.highlightsquare(row,col,"blue",'highlight') # Adding a blue edge around the square
                    self.square_text_x.set("Selected Square (x) = "+str(col+1)) # Indicating the selected square
                    self.square_text_y.set("Selected Square (y) = "+str(row+1))
                    # Then checking for what piece that is
                    found_key = []
                    if self.boardarray_pieces.loc[row,col] != 0:
                        found_key = self.boardarray_pieces.loc[row,col].getid()
                    if found_key == []:
                        occupier = "None"
                        self.validclick = False
                    else:
                        occupier = self.piece_description[found_key[0]]
                        self.validclick = True
                    self.desiredsquare = [row,col] # Saving this information in the desiredsquare variable
                    self.square_text_displaypiece.set("Selected Piece = "+occupier)
                    self.square_text_displaypiece_bybutton.set(occupier)

                    if self.initiated and found_key != []: # If a game has been started
                        self.visualisemoves(row,col,found_key) # Asking all possible moves to be displayed by calling this method
                else: # Otherwise if the click wasn't valid
                    self.canvas.delete("highlight") # Clear highlighting
                    self.canvas.delete("example")
                    self.highlightsquare(row,col,"red",'highlight') # Display a red edge

            else: # Otherwise we have clicked outside the board so we reset
                self.canvas.delete("move")  # Clearing all types of highlighting currently o the board
                self.canvas.delete("highlight")
                self.canvas.delete("example")
                self.square_text_x.set("Selected Square (x) = None")
                self.square_text_y.set("Selected Square (y) = None")
                self.square_text_displaypiece.set("Selected Piece = None")
        else:
            # If the square has been locked
            offset = self.square_virtual_size # This is the number required to make it work......
            col = math.floor(xcoords/offset)
            row = math.floor(ycoords/offset)
            target_squares = self.possiblemoves(self.desiredsquare[0],self.desiredsquare[1]) # Requesting the possible moves
            for plotter in target_squares: # Cycling through them all
                if plotter[0] == str(row) and plotter[1] == str(col): # Checking if the clicked square is one of them
                    self.canvas.delete("move") # Deleting previous highlights
                    self.highlightsquare(row,col,"green",'move') # Adding a new one in this square
                    self.movesquare = [row,col] # Setting the move square to the one clicked
                    self.summarylabel3.place(x=self.square_virtual_size * 8+50,y=self.controls_height+112,height=16) # Updating labels
                    self.summarylabel3_piece.place(x=self.square_virtual_size * 8+120,y=self.controls_height+112,height=16)
                    self.newsquare.set("[ "+str(self.movesquare[0]+1)+" , "+str(self.movesquare[1]+1)+" ]")
                    self.movebutton.config(state="normal") # Unlocking the move button

    def highlightsquare(self,row,col,colour,tag):
        # Recieves a square to put a box around
        offset = self.square_virtual_size # Finding the sze of a square
        if colour == "green": # If the colour requested is green we use a lighter colour
            colour = "#00cc00" # This is just a lighter green than the standard "green" color to make it clearer on the board
        self.canvas.create_line(col * offset,row * offset,col * offset+offset,row * offset,fill=colour,width=3,tag=tag) # Adding in the 4 lines
        self.canvas.create_line(col * offset,row * offset,col * offset,row * offset+offset,fill=colour,width=3,tag=tag)
        self.canvas.create_line(col * offset+offset,row * offset+offset,col * offset+offset,row * offset,fill=colour,width=3,tag=tag)
        self.canvas.create_line(col * offset+offset,row * offset+offset,col * offset,row * offset+offset,fill=colour,width=3,tag=tag)

    def visualisemoves(self,row,col,piece_code):
        self.canvas.delete("example") # Removes all previously highlighted possible moves
        offset = self.square_virtual_size
        target_squares = self.possiblemoves(row,col) # Requesting possible moves for the piece in that sqaure
        for plotter in target_squares: # Cycling through all squares
            self.highlightsquare(int(plotter[0]),int(plotter[1]),"orange","example") # Adding an orange box around them

    def possiblemoves(self,row,col):
        # This just puts a request in to the specific piece in that square
        squares = self.boardarray_pieces.loc[row,col].validsquares()
        return squares

    def addpiece(self, name, image, row, column):
        # We can add a piece to the board at the requested location
        self.canvas.create_image(0,0, image=image, tags=(name, "piece"), anchor="c") # First we create the image in the top left
        self.placepiece(name, row, column) # Then we move it to the specified location

    def removepiece(self, name):
        # This is only used when a piece is taken
        # This change is purely aesthetic
        self.canvas.delete(name) # Removes it based on a piece_id from a chesspiece object
        del self.pieces[name] # We also remove it from the pieces list

    def placepiece(self, name, row, col):
        '''Place a piece at the given row/column'''
        self.pieces[name] = (row,col) # Saves where it was placed
        x0 = (col * self.size) + int(self.size/2) # Works out where it should be in pixels
        y0 = (row * self.size) + int(self.size/2)
        self.canvas.coords(name, x0, y0) # Sets it to that location

    def defaults(self):
        '''Sets the board up for a fresh game'''
        self.start_button.config(state="normal")

        # We assume that the board is populated and so try to remove pieces from each square
        for row in range(0,8): # Through all squares
            for col in range(0,8):
                if self.boardarray_pieces.loc[row,col] != 0: # If the square isnt empty
                    self.removepiece(self.boardarray_pieces.loc[row,col].getid()) # Remove the image
        self.boardarray_pieces = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7]) # Reset the boardarray

        # Adding in pieces 1 by 1 and create the objects to store in boardarray
        # Castles
        r1 = ChessComponents.Rook("r1",0,0)
        r2 = ChessComponents.Rook("r2",0,7)
        R1 = ChessComponents.Rook("R1",7,0)
        R2 = ChessComponents.Rook("R2",7,7)
        self.addpiece("r1",self.imageholder["r"],0,0)
        self.boardarray_pieces.loc[0,0] = r1
        self.addpiece("r2",self.imageholder["r"],0,7)
        self.boardarray_pieces.loc[0,7] = r2
        self.addpiece("R1",self.imageholder["R"],7,0)
        self.boardarray_pieces.loc[7,0] = R1
        self.addpiece("R2",self.imageholder["R"],7,7)
        self.boardarray_pieces.loc[7,7] = R2
        # Naves
        n1 = ChessComponents.Knight("n1",0,1)
        n2 = ChessComponents.Knight("n2",0,6)
        N1 = ChessComponents.Knight("N1",7,1)
        N2 = ChessComponents.Knight("N2",7,6)
        self.addpiece("n1",self.imageholder["n"],0,1)
        self.boardarray_pieces.loc[0,1] = n1
        self.addpiece("n2",self.imageholder["n"],0,6)
        self.boardarray_pieces.loc[0,6] = n2
        self.addpiece("N1",self.imageholder["N"],7,1)
        self.boardarray_pieces.loc[7,1] = N1
        self.addpiece("N2",self.imageholder["N"],7,6)
        self.boardarray_pieces.loc[7,6] = N2
        # Bishops
        b1 = ChessComponents.Bishop("b1",0,2)
        b2 = ChessComponents.Bishop("b2",0,5)
        B1 = ChessComponents.Bishop("B1",7,2)
        B2 = ChessComponents.Bishop("B2",7,5)
        self.addpiece("b1",self.imageholder["b"],0,2)
        self.boardarray_pieces.loc[0,2] = b1
        self.addpiece("b2",self.imageholder["b"],0,5)
        self.boardarray_pieces.loc[0,5] = b2
        self.addpiece("B1",self.imageholder["B"],7,2)
        self.boardarray_pieces.loc[7,2] = B1
        self.addpiece("B2",self.imageholder["B"],7,5)
        self.boardarray_pieces.loc[7,5] = B2
        # Queens
        q1 = ChessComponents.Queen("q1",0,3)
        Q1 = ChessComponents.Queen("Q1",7,3)
        self.addpiece("q1",self.imageholder["q"],0,3)
        self.boardarray_pieces.loc[0,3] = q1
        self.addpiece("Q1",self.imageholder["Q"],7,3)
        self.boardarray_pieces.loc[7,3] = Q1
        # Kings
        k1 = ChessComponents.King("k1",0,4)
        K1 = ChessComponents.King("K1",7,4)
        self.addpiece("k1",self.imageholder["k"],0,4)
        self.boardarray_pieces.loc[0,4] = k1
        self.addpiece("K1",self.imageholder["K"],7,4)
        self.boardarray_pieces.loc[7,4] = K1
        # Pawns
        p1 = ChessComponents.Pawn("p1",1,0)
        p2 = ChessComponents.Pawn("p2",1,1)
        p3 = ChessComponents.Pawn("p3",1,2)
        p4 = ChessComponents.Pawn("p4",1,3)
        p5 = ChessComponents.Pawn("p5",1,4)
        p6 = ChessComponents.Pawn("p6",1,5)
        p7 = ChessComponents.Pawn("p7",1,6)
        p8 = ChessComponents.Pawn("p8",1,7)
        P1 = ChessComponents.Pawn("P1",6,0)
        P2 = ChessComponents.Pawn("P2",6,1)
        P3 = ChessComponents.Pawn("P3",6,2)
        P4 = ChessComponents.Pawn("P4",6,3)
        P5 = ChessComponents.Pawn("P5",6,4)
        P6 = ChessComponents.Pawn("P6",6,5)
        P7 = ChessComponents.Pawn("P7",6,6)
        P8 = ChessComponents.Pawn("P8",6,7)
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
        # This function
        self.initiated = True # Indicates that the game has started
        self.start_button.config(state="disabled") # Make it so the start button can't be pressed again
        self.player1.config(state="disabled") # Disabling the drop-down options
        self.player2.config(state="disabled")
        self.canvas.create_image(0,0, image=self.imageholder["lock"],tags="lock1", anchor="c") # Adding lock image
        self.canvas.create_image(0,0,image=self.imageholder["lock"],tags="lock2",anchor="c")
        self.canvas.coords("lock1",785,140)
        self.canvas.coords("lock2",785,160)
        self.current_turn_disp.set("White Pieces") # White starts first
        self.current_turn_text.config(fg="black",bg="white")
        # This line allows the opportunity to let a computer take a turn if there is a computer playing
        self.Autoplayer = ChessComponents.Comp1()
        if self.playmode1.get() == "Computer":
            self.Autoplayer.colour_ref = "White Pieces"
            self.Autoplayer.colour = "w"
        elif self.playmode2.get() == "Computer":
            self.Autoplayer.colour_ref = "Black Pieces"
            self.Autoplayer.colour = "b"
        self.calculateturn()

    def calculateturn(self):
        if self.Autoplayer.colour_ref == self.current_turn_disp.get():
            square1, square2 = self.Autoplayer.taketurn(self.boardarray_pieces,self.colourarray)
            self.desiredsquare = square1
            self.movesquare = square2
            self.movepiece()


    def lockselection(self):
        # Activated by the select piece button
        if self.validclick and self.squarechosen == False: # If the click was valid and a square hasn't been chosen
            self.squarechosen = True # Indicate a square is chosen
            self.selectbuttonstring.set("Deselect Piece") # Change the text to the opposite
            self.selected_displaypiece_bybutton.config(background="green") # Use green to indicate a selection has been made
            self.summarylabel1.place(x=self.square_virtual_size * 8+50,y=self.controls_height+84,height=16)
            self.oldsquare.set("[ "+str(self.desiredsquare[0]+1)+" , "+str(self.desiredsquare[1]+1)+" ]")
            self.summarylabel1.place(x=self.square_virtual_size * 8+50,y=self.controls_height+84,height=16)
            self.summarylabel2.place(x=self.square_virtual_size * 8+50,y=self.controls_height+98,height=16)
            self.summarylabel2_piece.place(x=self.square_virtual_size * 8+120,y=self.controls_height+98,height=16)
        elif self.squarechosen: # If a piece was already chosen then we want to deselect
            self.selectbuttonstring.set("Select Piece") # Revert the button
            self.selected_displaypiece_bybutton.config(background="bisque")
            self.oldsquare.set("") # Clear square text
            self.newsquare.set("")
            self.movebutton.config(state="disabled") # disable the move button
            self.squarechosen = False # Toggle square chosen
        else: # If neither cases are met then we do nothing
            return

    def movepiece(self):
        # First we check if their is a piece that needs to be removed
        if self.boardarray_pieces.loc[self.movesquare[0],self.movesquare[1]] != 0: # Is the square full
            self.removepiece(self.boardarray_pieces.loc[self.movesquare[0],self.movesquare[1]].getid()) # If so remove it
        self.placepiece(self.boardarray_pieces.loc[self.desiredsquare[0],self.desiredsquare[1]].getid(),self.movesquare[0],self.movesquare[1]) # Move the original piece
        self.boardarray_pieces.loc[self.movesquare[0],self.movesquare[1]] = self.boardarray_pieces.loc[self.desiredsquare[0],self.desiredsquare[1]] # Update boardarray
        self.boardarray_pieces.loc[self.desiredsquare[0],self.desiredsquare[1]] = 0 # Set the old square to empty
        self.colourarray.loc[self.desiredsquare[0],self.desiredsquare[1]] = 0 # Same for colour array
        self.colourarray.loc[self.movesquare[0],self.movesquare[1]] = self.boardarray_pieces.loc[self.movesquare[0],self.movesquare[1]].getcolour() # Set colour array to the piece colour
        self.boardarray_pieces.loc[self.movesquare[0],self.movesquare[1]].iterate() # Incriment a turn for the piece
        self.lockselection() # Press "deselect piece"
        self.canvas.delete("highlight") # Remove all highlighting
        self.canvas.delete("example")
        self.canvas.delete("move")
        # Allows for the the piece valid spaces to be updated by the latest move
        self.update_piecemoves()
        # Flip the turn
        if self.current_turn_check == "w":
            self.current_turn_disp.set("Black Pieces")
            self.current_turn_check = "b"
            self.current_turn_text.config(bg="black",fg="white")
        else:
            self.current_turn_disp.set("White Pieces")
            self.current_turn_check = "w"
            self.current_turn_text.config(fg="black",bg="white")
        # Invites the computer to take a turn
        self.calculateturn()

    def update_piecemoves(self):
        # Later on it would be good to add some optimisation here but for now it is enough to cycle though
        for row in range(0,8): # Through all rows
            for col in range(0,8): # And all columns
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