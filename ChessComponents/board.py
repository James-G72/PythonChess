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
        self.pieceDescription = {} # A dictionary used to relate the piece codes to readable descriptions for the user
        self.initiated = False # Has a game started and effects the interpretation of clicks on the canvas
        self.playerHolder = [0,0] # This is used to hold either stockfish or a custom algorithm [0] is w and [1] is b
        self.holderEnum = 0 # 0 represents white
        self.checkPiece = [] # When empty there is no check. It is populated with the square of the king in check
        self.checkMate = False

        # All of the piece objects are held within a pandas DataFrame in their relative locations.
        # This variable ultimately describes the state of the game
        self.boardArrayPieces = pd.DataFrame(np.zeros((self.rows,self.columns)),index=range(0,self.rows),columns=range(0,self.columns))
        # The boardarray variable is accompanied by a colourArray which contains only the colour information
        # This is done to make referencing simpler when calculating moves.
        # I am not sure how necessary this is but should be quicker ad eventually might be changed to enums to avoid string comparisons
        self.colourArray = pd.DataFrame(np.zeros((self.rows,self.columns)),index=range(0,self.rows),columns=range(0,self.columns))
        self.current_turn_disp = tk.StringVar() # Displays the piece group which is current goinng
        self.current_turn_disp.set("") # Blank label won't display anything at first
        self.current_turn_check = "w" # This regulates which pieces can be moved. White goes first

        self.desiredSquare = [] # This is the square that the player wants to move and is locked using the select piece button
        self.squareChosen = False # This is triggered when a square is chosen
        self.validClick = False # This allows the board to know if a valid square to move to has been selected or not. This is stored on this level as it effects labels
        self.moveSquare = [] # This is the square that the player wants to move to
        self.fullMove = 1 # Tracks how many moves there have been

        # Adding all of the pictures from Images folder
        self.imageHolder = {} # Creating a dictionary
        pieceList = "bknpqr" # These are all the different types of pieces possible
        colourList = "bw" # The two colours
        for f in pieceList: # Cycling through the pieces
            for l in colourList: # Alternating between the two colours
                with open("Images/"+f+l+".gif","rb") as imageFile: # Opening the photo within the variable space
                    # The images can't be stored as P or p in MacOS as theyre read the same
                    # So the colour is introduced by adding b or w after the piece notation
                    string = base64.b64encode(imageFile.read()) # Creating a string that describes the gif in base64 format
                if l == "w": # Checking if this is a white piece
                    # When adding the image to a dictionary we use proper notation and capitalise the letter if it is a white piece
                    self.imageHolder[f.capitalize()] = tk.PhotoImage(data=string)
                else:
                    # if it is a black piece then no change is required
                    self.imageHolder[f] = tk.PhotoImage(data=string)
        # An additional image is a picture of a padlock to show that variables are locked
        with open("Images/lock.gif","rb") as imageFile:
            string = base64.b64encode(imageFile.read())
        self.imageHolder["lock"] = tk.PhotoImage(data=string) # The picture is simply called lock in the dictionary

        # To help convert between FEN and the row/col notation used for our board we create a DataFrame with the conversions
        self.FENConversionCol = pd.DataFrame(np.zeros((1,8)),index=["Board"],columns=["a","b","c","d","e","f","g","h"])
        self.FENConversionRow = pd.DataFrame(np.zeros((1,8)),index=["Board"],columns=["1","2","3","4","5","6","7","8"])
        self.FENConversionCol.loc["Board",:] = [0,1,2,3,4,5,6,7]
        self.FENConversionRow.loc["Board",:] = [7,6,5,4,3,2,1,0]
        self.debug_set = False # This is a debugger toggle used to set the board to any state for testing

        # Adding text for piece descriptions to a dictionary which is then displayed to the user via a label
        # This helps to explain the notation going on above and is designed to be compatible with FEN
        # https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation
        self.pieceDescription["r"] = "Black Castle"
        self.pieceDescription["R"] = "White Castle"
        self.pieceDescription["b"] = "Black Bishop"
        self.pieceDescription["B"] = "White Bishop"
        self.pieceDescription["k"] = "Black King"
        self.pieceDescription["K"] = "White King"
        self.pieceDescription["n"] = "Black Knight"
        self.pieceDescription["N"] = "White Knight"
        self.pieceDescription["q"] = "Black Queen"
        self.pieceDescription["Q"] = "White Queen"
        self.pieceDescription["p"] = "Black Pawn"
        self.pieceDescription["P"] = "White Pawn"

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
        # Adding a debug mode toggle which allows an FEN board to be set from a box
        self.debug_button = tk.Button(self,text="Debug", fg="blue", font=("TKDefaultFont",8), command=self.Debug)
        self.debug_button.place(x=self.square_virtual_size*8 + self.side_size-24, y=self.square_virtual_size*8, height=10)

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
        self.player1 = tk.OptionMenu(self,self.playmode1,"Person","Computer","Random")
        self.player1.place(x=self.square_virtual_size*8 + 80, y=self.playmode_height+45, height=16)
        self.player1.config(background="bisque") # For optionmenu the bg abbreviation means in the dropdown
        self.player2 = tk.OptionMenu(self,self.playmode2,"Person","Computer","Random")
        self.player2.place(x=self.square_virtual_size * 8+80,y=self.playmode_height+65,height=16)
        self.player2.config(background="bisque") # For optionmenu the bg abbreviation means in the dropdown

        # Start and reset button
        self.reset_button = tk.Button(self,text="Reset Board",bg="black", command=self.Defaults)
        self.reset_button.place(x=self.square_virtual_size*8 + 115, y=202, height=16)
        self.start_button = tk.Button(self,text="Start!",fg="green",background="black",font=("TKDefaultFont",30), command=self.Initiate)
        self.start_button.place(x=self.square_virtual_size * 8+20,y=196,height=28)

        # Adding controls section to allow the game to be played
        self.controls_height = 225
        self.canvas.create_rectangle(self.square_virtual_size*8 + 4,self.controls_height,self.square_virtual_size*8 + 10+192,self.controls_height+160,width=2)
        self.controls_heading = tk.Label(self,text="Controls:",font=("TKDefaultFont",18),bg="bisque")
        self.controls_heading.place(x=self.square_virtual_size*8 + 70, y=self.controls_height+15, height=16)
        self.selectbuttonstring = tk.StringVar()
        self.selectbuttonstring.set("Select Piece")
        self.select_button = tk.Button(self,textvariable=self.selectbuttonstring,fg="black",background="black",font=("TKDefaultFont",12), command=self.LockSelection)
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

        self.movebutton = tk.Button(self,text="Move Piece",fg="black",background="black",font=("TKDefaultFont",22), command=self.MovePiece)
        self.movebutton.place(x=self.square_virtual_size * 8+50,y=self.controls_height+144,height=20)
        self.movebutton.config(state="disabled")

        # Current turn indicator
        self.current_turn_indicator = tk.Label(self,text="Current Turn:",font=("TKDefaultFont",12),bg="bisque")
        self.current_turn_indicator.place(x=self.square_virtual_size * 8+60,y=400,height=20)
        self.current_turn_text = tk.Label(self,textvariable=self.current_turn_disp,font=("TKDefaultFont",16),bg="bisque")
        self.current_turn_text.place(x=self.square_virtual_size * 8+52,y=422,height=20)

        # Binding configuration and left mouse click
        self.canvas.bind("<Button 1>",self.GetCoords) # This allows the clicking to be tracked
        # If a the user changes the window size then the refresh call is made. This is defined below
        self.canvas.bind("<Configure>", self.refresh) # This shouldn't happen as the size has been locked

    def GetCoords(self, event):
        global x0,y0
        x0 = event.x # Event is a click
        y0 = event.y
        # This retrieves the current x and y coordinates in terms of pixels from the top left
        if self.initiated: # If the game is started....
            self.SelectSquare(x0,y0) # This information is passed into the SelectSquare method

    def SelectSquare(self, xcoords, ycoords):
        valid = False # Allows the alternating turns of the two players to be observed
        offset = self.square_virtual_size  # This is the number required to make it work......
        col = math.floor(xcoords / offset) # Finding the square the player means
        row = math.floor(ycoords / offset)
        if self.squareChosen == False: # If we haven't chosen one yet then choose one
            if col <= 7 and row <= 7: # Have we clicked within the bounds of the board
                if self.current_turn_check == "w" and self.colourArray.loc[row,col] != "b": # Checking if it is the right colour
                    valid = True # Allowing access to additional code
                elif self.current_turn_check == "b" and self.colourArray.loc[row,col] != "w":
                    valid = True
                if valid:
                    self.canvas.delete("move") # Clearing all types of highlighting currently o the board
                    self.canvas.delete("highlight")
                    self.canvas.delete("example")
                    self.HighlightSquare(row,col,"blue",'highlight') # Adding a blue edge around the square
                    self.square_text_x.set("Selected Square (x) = "+str(col+1)) # Indicating the selected square
                    self.square_text_y.set("Selected Square (y) = "+str(row+1))
                    # Then checking for what piece that is
                    found_key = []
                    if self.boardArrayPieces.loc[row,col] != 0:
                        found_key = self.boardArrayPieces.loc[row,col].getid()
                    if found_key == []:
                        occupier = "None"
                        self.validClick = False
                    else:
                        occupier = self.pieceDescription[found_key[0]]
                        self.validClick = True
                    self.desiredSquare = [row,col] # Saving this information in the desiredSquare variable
                    self.square_text_displaypiece.set("Selected Piece = "+occupier)
                    self.square_text_displaypiece_bybutton.set(occupier)

                    if self.initiated and found_key != []: # If a game has been started
                        self.VisualiseMoves(row,col,found_key) # Asking all possible moves to be displayed by calling this method
                else: # Otherwise if the click wasn't valid
                    self.canvas.delete("highlight") # Clear highlighting
                    self.canvas.delete("example")
                    self.HighlightSquare(row,col,"red",'highlight') # Display a red edge

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
            target_squares = self.PossibleMoves(self.desiredSquare[0],self.desiredSquare[1]) # Requesting the possible moves
            for plotter in target_squares: # Cycling through them all
                if plotter[0] == str(row) and plotter[1] == str(col): # Checking if the clicked square is one of them
                    self.canvas.delete("move") # Deleting previous highlights
                    self.HighlightSquare(row,col,"green",'move') # Adding a new one in this square
                    self.moveSquare = [row,col] # Setting the move square to the one clicked
                    self.summarylabel3.place(x=self.square_virtual_size * 8+50,y=self.controls_height+112,height=16) # Updating labels
                    self.summarylabel3_piece.place(x=self.square_virtual_size * 8+120,y=self.controls_height+112,height=16)
                    self.newsquare.set("[ "+str(self.moveSquare[0]+1)+" , "+str(self.moveSquare[1]+1)+" ]")
                    self.movebutton.config(state="normal") # Unlocking the move button

    def HighlightSquare(self,row,col,colour,tag):
        # Recieves a square to put a box around
        offset = self.square_virtual_size # Finding the sze of a square
        if colour == "green": # If the colour requested is green we use a lighter colour
            colour = "#00cc00" # This is just a lighter green than the standard "green" color to make it clearer on the board
        self.canvas.create_line(col * offset,row * offset,col * offset+offset,row * offset,fill=colour,width=3,tag=tag) # Adding in the 4 lines
        self.canvas.create_line(col * offset,row * offset,col * offset,row * offset+offset,fill=colour,width=3,tag=tag)
        self.canvas.create_line(col * offset+offset,row * offset+offset,col * offset+offset,row * offset,fill=colour,width=3,tag=tag)
        self.canvas.create_line(col * offset+offset,row * offset+offset,col * offset,row * offset+offset,fill=colour,width=3,tag=tag)

    def VisualiseMoves(self,row,col,piece_code):
        self.canvas.delete("example") # Removes all previously highlighted possible moves
        offset = self.square_virtual_size
        target_squares = self.PossibleMoves(row,col) # Requesting possible moves for the piece in that sqaure
        for plotter in target_squares: # Cycling through all squares
            self.HighlightSquare(int(plotter[0]),int(plotter[1]),"orange","example") # Adding an orange box around them

    def PossibleMoves(self,row,col):
        # This just puts a request in to the specific piece in that square
        squares = self.boardArrayPieces.loc[row,col].validsquares()
        return squares

    def AddPiece(self, name, image, row, column):
        # We can add a piece to the board at the requested location
        self.canvas.create_image(0,0, image=image, tags=(name, "piece"), anchor="c") # First we create the image in the top left
        self.PlacePiece(name, row, column) # Then we move it to the specified location

    def RemovePiece(self, name):
        # This is only used when a piece is taken
        # This change is purely aesthetic
        self.canvas.delete(name) # Removes it based on a piece_id from a chesspiece object
        del self.pieces[name] # We also remove it from the pieces list

    def PlacePiece(self, name, row, col):
        '''Place a piece at the given row/column'''
        self.pieces[name] = (row,col) # Saves where it was placed
        x0 = (col * self.size) + int(self.size/2) # Works out where it should be in pixels
        y0 = (row * self.size) + int(self.size/2)
        self.canvas.coords(name, x0, y0) # Sets it to that location

    def Defaults(self):
        '''Sets the board up for a fresh game'''
        self.start_button.config(state="normal")

        # We assume that the board is populated and so try to remove pieces from each square
        for row in range(0,8): # Through all squares
            for col in range(0,8):
                if self.boardArrayPieces.loc[row,col] != 0: # If the square isnt empty
                    self.RemovePiece(self.boardArrayPieces.loc[row,col].getid()) # Remove the image
        self.boardArrayPieces = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7]) # Reset the boardarray

        # Adding in pieces 1 by 1 and create the objects to store in boardarray
        # Castles
        r1 = ChessComponents.Rook("r1",0,0)
        r2 = ChessComponents.Rook("r2",0,7)
        R1 = ChessComponents.Rook("R1",7,0)
        R2 = ChessComponents.Rook("R2",7,7)
        self.AddPiece("r1",self.imageHolder["r"],0,0)
        self.boardArrayPieces.loc[0,0] = r1
        self.AddPiece("r2",self.imageHolder["r"],0,7)
        self.boardArrayPieces.loc[0,7] = r2
        self.AddPiece("R1",self.imageHolder["R"],7,0)
        self.boardArrayPieces.loc[7,0] = R1
        self.AddPiece("R2",self.imageHolder["R"],7,7)
        self.boardArrayPieces.loc[7,7] = R2
        # Naves
        n1 = ChessComponents.Knight("n1",0,1)
        n2 = ChessComponents.Knight("n2",0,6)
        N1 = ChessComponents.Knight("N1",7,1)
        N2 = ChessComponents.Knight("N2",7,6)
        self.AddPiece("n1",self.imageHolder["n"],0,1)
        self.boardArrayPieces.loc[0,1] = n1
        self.AddPiece("n2",self.imageHolder["n"],0,6)
        self.boardArrayPieces.loc[0,6] = n2
        self.AddPiece("N1",self.imageHolder["N"],7,1)
        self.boardArrayPieces.loc[7,1] = N1
        self.AddPiece("N2",self.imageHolder["N"],7,6)
        self.boardArrayPieces.loc[7,6] = N2
        # Bishops
        b1 = ChessComponents.Bishop("b1",0,2)
        b2 = ChessComponents.Bishop("b2",0,5)
        B1 = ChessComponents.Bishop("B1",7,2)
        B2 = ChessComponents.Bishop("B2",7,5)
        self.AddPiece("b1",self.imageHolder["b"],0,2)
        self.boardArrayPieces.loc[0,2] = b1
        self.AddPiece("b2",self.imageHolder["b"],0,5)
        self.boardArrayPieces.loc[0,5] = b2
        self.AddPiece("B1",self.imageHolder["B"],7,2)
        self.boardArrayPieces.loc[7,2] = B1
        self.AddPiece("B2",self.imageHolder["B"],7,5)
        self.boardArrayPieces.loc[7,5] = B2
        # Queens
        q1 = ChessComponents.Queen("q1",0,3)
        Q1 = ChessComponents.Queen("Q1",7,3)
        self.AddPiece("q1",self.imageHolder["q"],0,3)
        self.boardArrayPieces.loc[0,3] = q1
        self.AddPiece("Q1",self.imageHolder["Q"],7,3)
        self.boardArrayPieces.loc[7,3] = Q1
        # Kings
        k1 = ChessComponents.King("k1",0,4)
        K1 = ChessComponents.King("K1",7,4)
        self.AddPiece("k1",self.imageHolder["k"],0,4)
        self.boardArrayPieces.loc[0,4] = k1
        self.AddPiece("K1",self.imageHolder["K"],7,4)
        self.boardArrayPieces.loc[7,4] = K1
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
            self.AddPiece("p"+str(x+1),self.imageHolder["p"],1,x)
            self.AddPiece("P"+str(x+1),self.imageHolder["P"],6,x)
        self.boardArrayPieces.loc[1,0] = p1
        self.boardArrayPieces.loc[1,1] = p2
        self.boardArrayPieces.loc[1,2] = p3
        self.boardArrayPieces.loc[1,3] = p4
        self.boardArrayPieces.loc[1,4] = p5
        self.boardArrayPieces.loc[1,5] = p6
        self.boardArrayPieces.loc[1,6] = p7
        self.boardArrayPieces.loc[1,7] = p8
        self.boardArrayPieces.loc[6,0] = P1
        self.boardArrayPieces.loc[6,1] = P2
        self.boardArrayPieces.loc[6,2] = P3
        self.boardArrayPieces.loc[6,3] = P4
        self.boardArrayPieces.loc[6,4] = P5
        self.boardArrayPieces.loc[6,5] = P6
        self.boardArrayPieces.loc[6,6] = P7
        self.boardArrayPieces.loc[6,7] = P8

        # Updating the colourArray position
        self.colourArray = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7])
        self.colourArray.loc[0:1,:] = "b"
        self.colourArray.loc[6:7,:] = "w"

        self.player1.config(state="normal")  # Enabling the drop-down options
        self.player2.config(state="normal")
        self.canvas.delete("lock1") # Removing the lock symbol if its there
        self.canvas.delete("lock2")
        self.initiated = False # Essentially saying that the game is no longer active

    def Debug(self): # Has 2 modes depending on the polarity of set
        if self.debug_set == True: # Then we excecute the contents of the text box
            FEN_requested = self.debug_text.get()
            if FEN_requested != "": # This means nothing has been entered into the field.
                # I feel its best to use a try here as it is quite likely that something wrong will be entered.
                self.SetBoardfromFEN(FEN_requested)

            self.debug_text.destroy()
            self.debug_set = False # Toggle
        else: # Then we display the text box and button
            self.debug_text = tk.Entry(self, font=("TKDefaultFont",8))
            self.debug_text.place(x=self.square_virtual_size * 8+15, y=self.square_virtual_size * 8-15, height=10)
            self.debug_set = True # Toggle

    def Initiate(self):
        # This function starts the game upon request
        self.initiated = True # Indicates that the game has started
        self.start_button.config(state="disabled") # Make it so the start button can't be pressed again
        self.player1.config(state="disabled") # Disabling the drop-down options
        self.player2.config(state="disabled")
        self.canvas.create_image(0,0, image=self.imageHolder["lock"],tags="lock1", anchor="c") # Adding lock image
        self.canvas.create_image(0,0,image=self.imageHolder["lock"],tags="lock2",anchor="c")
        self.canvas.coords("lock1",785,140)
        self.canvas.coords("lock2",785,160)
        if self.current_turn_check == "w":
            self.current_turn_disp.set("White Pieces") # White starts first
            self.current_turn_text.config(fg="black",bg="white")
        else:
            self.current_turn_disp.set("Black Pieces") # White starts first
            self.current_turn_text.config(fg="white",bg="black")
        # This line allows the opportunity to let a computer take a turn if there is a computer playing
        autoPlayer = ChessComponents.Comp1()
        # This is a very complex line that uses a stockfish wrapper to allow stockfish to play the game
        stockfish = ChessComponents.Stockfish("/Users/jamesgower2/Documents/Stockfish-master/src/stockfish")
        stockfish.set_fen_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        if self.playmode1.get() == "Computer":
            self.playerHolder[0] = stockfish
        elif self.playmode1.get() == "Random":
            autoPlayer.colour_ref = "White Pieces"
            autoPlayer.colour = "w"
            self.playerHolder[0] = autoPlayer
        if self.playmode2.get() == "Computer":
            self.playerHolder[1] = stockfish
        elif self.playmode2.get() == "Random":
            autoPlayer.colour_ref = "Black Pieces"
            autoPlayer.colour = "b"
            self.playerHolder[1] = autoPlayer
        self.CalculateTurn()

    def CalculateTurn(self):
        if self.playerHolder[self.holderEnum] != 0: # Then the turn is automatic
            if self.playerHolder[self.holderEnum].getid() == "Stockfish":
                # We also want to tell the stockfish engine what the latest move is
                # I tried doing this via the set_position method but it doest work so will now try passing full FEN in
                current = self.playerHolder[self.holderEnum].get_fen_position()
                self.playerHolder[self.holderEnum].set_fen_position(self.FENConvert("FullFEN"))
                current = self.playerHolder[self.holderEnum].get_fen_position()
                stockfishMove = self.playerHolder[self.holderEnum].get_best_move()
                self.desiredSquare, self.moveSquare = self.FENConvert("SAN2Board",stockfishMove)
                # Having performed the FEN conversion the desired square and move square should have been set correctly
            else:
                self.desiredSquare, self.moveSquare = self.playerHolder[self.holderEnum].taketurn(self.boardArrayPieces,self.colourArray)
            self.MovePiece()
        else: # This is needed to unlock the selection before a players turn
            self.LockSelection()

    def FENConvert(self,direction,target=None):
        # This method converts the current board position to FEN or a stockfish move to a move in the notation used for this board
        # In SAN the position "a1" is located at the bottom left of the board in the white corner
        # For the row/col notation used here a1 corresponds to row = 7, col = 0. h8 -> row = 0, col = 7
        if direction == "SAN2Board": # Converting an FEN move to one readable by the board
            des = target[0:2] # Desired move in FEN
            mov = target[2:4] # Desired move in FEN
            return [int(self.FENConversionRow.loc["Board",des[1]]),int(self.FENConversionCol.loc["Board",des[0]])] , [int(self.FENConversionRow.loc["Board",mov[1]]),int(self.FENConversionCol.loc["Board",mov[0]])]
        elif direction == "Board2SAN": # Converting a player move to one readable by stockfish
            des = self.desiredSquare
            mov = self.moveSquare
            # There is probably a better way to reverse search a dataframe but this works
            row1 = self.FENConversionRow.columns[np.flatnonzero(self.FENConversionRow.loc["Board",:] == des[0])[0]]
            col1 = self.FENConversionCol.columns[np.flatnonzero(self.FENConversionCol.loc["Board",:] == des[1])[0]]
            row2 = self.FENConversionRow.columns[np.flatnonzero(self.FENConversionRow.loc["Board",:] == mov[0])[0]]
            col2 = self.FENConversionCol.columns[np.flatnonzero(self.FENConversionCol.loc["Board",:] == mov[1])[0]]
            return str(col1)+str(row1)+str(col2)+str(row2) # Returning a
        elif direction == "FullFEN":
            # Here we create a FEN string such as this one: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1"
            FEN = ""
            for r in range(0,8):
                empties = 0
                for c in range(0,8):
                    if self.boardArrayPieces.loc[r,c] != 0:
                        if empties > 0:
                            FEN += str(empties)
                            empties = 0
                        FEN += self.boardArrayPieces.loc[r,c].getid()[0]
                    else:
                        empties += 1
                if empties > 0:
                    FEN += str(empties)
                if c != r != 7:
                    FEN += "/"
            FEN += " "+str(self.current_turn_check)
            # Need to add in a valid castling check but for now assume all castling possible
            FEN += " KQkq "
            # Adding En Passent square
            if self.boardArrayPieces.loc[self.desiredSquare[0],self.desiredSquare[1]] != 0:
                if self.boardArrayPieces.loc[self.desiredSquare[0],self.desiredSquare[1]].getid()[0] == "P" or self.boardArrayPieces.loc[self.desiredSquare[0],self.desiredSquare[1]].getid()[0] == "p":
                    FEN += self.FENConversionCol.columns[np.flatnonzero(self.FENConversionCol.loc["Board",:] == self.moveSquare[1])[0]]
                    FEN += str((int(self.FENConversionRow.columns[np.flatnonzero(self.FENConversionRow.loc["Board",:] == self.moveSquare[0])[0]])+int(self.FENConversionRow.columns[np.flatnonzero(self.FENConversionRow.loc["Board",:] == self.desiredSquare[0])[0]]))/2)
                else:
                    FEN += "-"
            else:
                FEN += "-"
            # Finally the halfmoves and fullmoves are added
            FEN += " 0 "+str(self.fullMove)
            return FEN

    def SetBoardfromFEN(self,FEN_requested):
        # This is a reasonably rare task so we will encorperate it all into one function
        # Due to the board needing for objects to be created individually e.g. r1 for a rook we need all pieces to be present and then we can move them
        self.Defaults() # Full reset
        storage = pd.DataFrame(np.zeros((2,16))) # Temporarily hold all the pieces
        self.colourArray = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7])
        counter = 0
        for row in [0,1,6,7]:
            for col in range(0,8):
                if row < 2:
                    storage.loc[0,counter] = self.boardArrayPieces.loc[row,col]
                    self.RemovePiece(self.boardArrayPieces.loc[row,col].getid())  # Remove the image
                    self.boardArrayPieces.loc[row,col] = 0
                    counter += 1
                else:
                    storage.loc[1,counter-16] = self.boardArrayPieces.loc[row,col]
                    self.RemovePiece(self.boardArrayPieces.loc[row,col].getid())  # Remove the image
                    self.boardArrayPieces.loc[row,col] = 0
                    counter += 1
        if FEN_requested[0].isnumeric():
            delay = int(FEN_requested[0])
        else:
            delay = 0
        counter = 0
        for row in range(0,self.rows):
            if row != 0 and col != 0:
                counter += 1 # We iterate the counter here as we need to skip over all slashes
            for col in range(0,self.columns):
                if delay > 0:
                    delay -= 1
                else:
                    if FEN_requested[counter].isnumeric():
                        delay = int(FEN_requested[counter])-1
                        counter += 1
                    else:
                        piece = FEN_requested[counter] # A FEN letter
                        counter += 1
                        if piece.isupper():
                            row_stor = 1
                        else:
                            row_stor = 0
                        for col_stor in range(0,storage.shape[1]):
                            if storage.loc[row_stor,col_stor] != 0:
                                if storage.loc[row_stor,col_stor].getid()[0] == piece:
                                    self.boardArrayPieces.loc[row,col] = storage.loc[row_stor,col_stor]
                                    self.AddPiece(storage.loc[row_stor,col_stor].getid(),self.imageHolder[storage.loc[row_stor,col_stor].getid()[0]],row,col)
                                    storage.loc[row_stor,col_stor] = 0
                                    if row_stor == 1: # Then it's a white piece
                                        self.colourArray.loc[row,col] = "w"
                                    else:
                                        self.colourArray.loc[row,col] = "b"
                                    break
        try:
            if FEN_requested[counter+1] == "b" or FEN_requested[counter+1] == "w":
                self.current_turn_check = FEN_requested[counter+1] # Setting the starting turn
        except:
            pass
        self.UpdatePieceMoves()

    def LockSelection(self):
        # Activated by the select piece button
        if self.validClick and self.squareChosen == False: # If the click was valid and a square hasn't been chosen
            self.squareChosen = True # Indicate a square is chosen
            self.selectbuttonstring.set("Deselect Piece") # Change the text to the opposite
            self.selected_displaypiece_bybutton.config(background="green") # Use green to indicate a selection has been made
            self.summarylabel1.place(x=self.square_virtual_size * 8+50,y=self.controls_height+84,height=16)
            self.oldsquare.set("[ "+str(self.desiredSquare[0]+1)+" , "+str(self.desiredSquare[1]+1)+" ]")
            self.summarylabel1.place(x=self.square_virtual_size * 8+50,y=self.controls_height+84,height=16)
            self.summarylabel2.place(x=self.square_virtual_size * 8+50,y=self.controls_height+98,height=16)
            self.summarylabel2_piece.place(x=self.square_virtual_size * 8+120,y=self.controls_height+98,height=16)
        elif self.squareChosen: # If a piece was already chosen then we want to deselect
            self.selectbuttonstring.set("Select Piece") # Revert the button
            self.selected_displaypiece_bybutton.config(background="bisque")
            self.oldsquare.set("") # Clear square text
            self.newsquare.set("")
            self.movebutton.config(state="disabled") # disable the move button
            self.squareChosen = False # Toggle square chosen
        else: # If neither cases are met then we do nothing
            return

    def MovePiece(self):
        # First we check if their is a piece that needs to be removed
        if self.boardArrayPieces.loc[self.moveSquare[0],self.moveSquare[1]] != 0: # Is the square full
            self.RemovePiece(self.boardArrayPieces.loc[self.moveSquare[0],self.moveSquare[1]].getid()) # If so remove it
        self.PlacePiece(self.boardArrayPieces.loc[self.desiredSquare[0],self.desiredSquare[1]].getid(),self.moveSquare[0],self.moveSquare[1]) # Move the original piece
        self.boardArrayPieces.loc[self.moveSquare[0],self.moveSquare[1]] = self.boardArrayPieces.loc[self.desiredSquare[0],self.desiredSquare[1]] # Update boardarray
        self.boardArrayPieces.loc[self.desiredSquare[0],self.desiredSquare[1]] = 0 # Set the old square to empty
        self.colourArray.loc[self.desiredSquare[0],self.desiredSquare[1]] = 0 # Same for colour array
        self.colourArray.loc[self.moveSquare[0],self.moveSquare[1]] = self.boardArrayPieces.loc[self.moveSquare[0],self.moveSquare[1]].getcolour() # Set colour array to the piece colour
        self.boardArrayPieces.loc[self.moveSquare[0],self.moveSquare[1]].iterate() # Increment a turn for the piece
        self.canvas.delete("highlight") # Remove all highlighting
        self.canvas.delete("example")
        self.canvas.delete("move")
        # Allows for the the piece valid spaces to be updated by the latest move. This also checks to see if either king is in check
        check = self.UpdatePieceMoves()
        if check:
            # Then 1 of the kings is in check. This should only ever be 1 piece
            # We know which king by the attacks array but it should also only ever be the king whos turn it currently is
            if self.boardArrayPieces.loc[self.checkPiece[0][0],self.checkPiece[0][1]].validsquares() == []:
                # Setting both the king piece checkMate marker and the board check mate marker to true
                self.boardArrayPieces.loc[self.checkPiece[0][0],self.checkPiece[0][1]].checkMate = True
                self.Checkmate()
        # Flip the turn
        if self.current_turn_check == "w":
            self.current_turn_disp.set("Black Pieces")
            self.current_turn_check = "b"
            self.current_turn_text.config(bg="black",fg="white")
            self.holderEnum += 1
        else:
            self.current_turn_disp.set("White Pieces")
            self.current_turn_check = "w"
            self.current_turn_text.config(fg="black",bg="white")
            self.fullMove += 1 # This is iterated after black has played their move
            self.holderEnum -= 1
        # Invites the computer to take a turn
        self.CalculateTurn()

    def UpdatePieceMoves(self):
        # Later on it would be good to add some optimisation here but for now it is enough to cycle though
        check_temp = False
        check = False
        self.checkPiece = []
        self.checkMate = False
        for row in range(0,8): # Through all rows
            for col in range(0,8): # And all columns
                if self.boardArrayPieces.loc[row,col] != 0: # If the space is blank we ship it
                    # Otherwise we call the update function in each of the pieces
                    self.boardArrayPieces.loc[row,col].updatemoves(row,col,self.boardArrayPieces,self.colourArray)
        # A quirk of doing it this way is that the piece moves need to be updated for checkCheck to work.
        # This also means that the kings move updates have to happen after all other pieces have been updated
        for row in range(0,8):  # Through all rows
            for col in range(0,8):  # And all columns
                if self.boardArrayPieces.loc[row,col] != 0:  # If the space is blank we ship it
                    if self.boardArrayPieces.loc[row,col].getid()[0] == "K" or self.boardArrayPieces.loc[row,col].getid()[0] == "k":
                        self.boardArrayPieces.loc[row,col].updatemoves(row,col,self.boardArrayPieces,self.colourArray)
                        check_temp, attacks = self.boardArrayPieces.loc[row,col].checkCheck(self.boardArrayPieces,row,col)
                        if check_temp:
                            check = True
                            self.checkPiece = attacks


        return check

    def Checkmate(self):
        self.checkMate = True
        self.wins_message = tk.Label(self,text=self.current_turn_disp.get()[0:5]+" Wins!",font=("TKDefaultFont",86),bg="bisque") # Display winner in big letters
        self.wins_message.place(x=self.square_virtual_size * 1.5,y=270,height=90)


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
            self.PlacePiece(name, self.pieces[name][0], self.pieces[name][1])
        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("square")