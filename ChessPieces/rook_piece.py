import pandas as pd
import numpy as np

class Rook():
    def __init__(self,piece_id,row,col):
        # Initialising the piece as a king
        self.turns = 0
        self.type = piece_id[0] # pnkbqrPNKBQR
        self.id = piece_id[1] # Number
        if self.type.isupper():
            self.colour = "w" # White
        else:
            self.colour = "b" # Black
        self.check = False

        self.moves = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7])
        # There are no moves to initialise so we can leave the matrix blank

    def getid(self):
        # Returns the id that corresponds to the correct image
        return self.type+self.id

    def getcolour(self):
        return self.colour

    def iterate(self):
        self.turns += 1

    def updatemoves(self,row,col,boardarray,colourarray):
        # To check all possible squares we need to search the row and column that the castle sits in
        # This is pretty unoptimised at the moment but this probably won't interact with the algorithm so will only be triggered after each move
        self.moves = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7])
        # First we'll check the rows
        for dif in [-1,1]: # Going up from the row and down
            checkrow = row+dif
            free = True
            while 0 <= checkrow <= 7 and free:
                if colourarray.loc[checkrow,col] == 0: # The square is free
                    self.moves.loc[checkrow,col] = 1
                elif colourarray.loc[checkrow,col] == self.colour:
                    free = False
                else:
                    self.moves.loc[checkrow,col] = 1
                    free = False
                checkrow += dif
        # Then we check all of the columnns
        for dif in [-1,1]: # Going up from the row and down
            checkcol = col+dif
            free = True
            while 0 <= checkcol <= 7 and free:
                if colourarray.loc[row,checkcol] == 0: # The square is free
                    self.moves.loc[row,checkcol] = 1
                elif colourarray.loc[row,checkcol] == self.colour:
                    free = False
                else:
                    self.moves.loc[row,checkcol] = 1
                    free = False
                checkcol += dif



    def validsquares(self):
        # This method packs the current valid moves into a simple
        squares_array = []
        for row in self.moves.index:
            for col in self.moves.columns:
                if self.moves.loc[row,col]:
                    squares_array.append(str(row)+str(col))
        return squares_array
