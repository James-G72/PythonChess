import pandas as pd
import numpy as np

class Pawn():
    def __init__(self,piece_id,row,col):
        # Initialising the piece
        self.turns = 0 # Hasn't been moved (this is most useful for the pawns)
        self.type = piece_id[0] # pnkbqrPNKBQR
        self.id = piece_id[1] # Number
        if self.type.isupper():
            self.colour = "w" # White
        else:
            self.colour = "b" # Black
        self.check = False

        # This is the key piece of information
        self.moves = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7])
        if self.colour == "w":
            self.moves.loc[col,4:5] = 1
        else:
            self.moves.loc[col,2:3] = 1

    def getid(self):
        # This is used for the placepiece method such that the correct image can be displayed
        return self.type+self.id

    def getcolour(self):
        return self.colour

    def iterate(self):
        self.turns += 1

    def updatemoves(self,row,col,boardarray,colourarray):
        # row and col essentially tell the piece where it is
        if self.colour == "w":
            checkrow = row+1
        else:
            checkrow = row-1
        if colourarray.loc[checkrow,col] == 0:
            self.moves.loc[checkrow,col] = 1
            if self.turns == 0: # Then the pawn has moved and therefore cannot move twice
                if colourarray.loc[checkrow+1,col] == 0:
                    self.moves.loc[checkrow+1,col] = 1
                else:
                    self.moves.loc[checkrow+1,col] = 0
        for checkcol in [col-1,col+1]:
            if checkcol >=0 and checkcol <=7:
                if colourarray.loc[checkrow,checkcol] != self.colour and colourarray.loc[checkrow,checkcol] != 0:
                    self.moves.loc[checkrow,checkcol] = 1
                else:
                    self.moves.loc[checkrow,checkcol] = 0
                if colourarray.loc[checkrow,col+1] != self.colour and colourarray.loc[checkrow,checkcol] != 0:
                    self.moves.loc[checkrow,checkcol] = 1
                else:
                    self.moves.loc[checkrow,checkcol] = 0

    def validsquares(self):
        # This method packs the current valid moves into a simple
        squares_array = []
        for y in self.moves.index:
            for x in self.moves.columns:
                if self.moves.loc[x,y]:
                    squares_array.append(str(x)+str(y))
        return squares_array
