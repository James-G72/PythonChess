import pandas as pd
import numpy as np

class King():
    def __init__(self,piece_id,row,col):
        # Initialising the piece
        self.turns = 0
        self.type = piece_id[0] # pnkbqrPNKBQR
        self.id = piece_id[1] # Number
        if self.type.isupper():
            self.colour = "w" # White
        else:
            self.colour = "b" # Black
        self.check = False

        self.moves = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7])

    def getid(self):
        # Returns the id that corresponds to the correct image
        return self.type+self.id

    def getcolour(self):
        return self.colour

    def iterate(self):
        self.turns += 1

    def updatemoves(self,row,col,boardarray,colourarray):
        # The king is possibly the simplest piece to move
        # Castling hasn't been implemented yet
        self.moves = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7])
        for row_dif in [-1,0,1]:  # Going up from the row and then down
            for col_dif in [-1,0,1]:  # Going up from the column and then down
                comp = row_dif==0 and col_dif==0
                if 0 <= row+row_dif <= 7 and 0 <= col+col_dif <= 7 and not comp:
                    if colourarray.loc[row+row_dif,col+col_dif] == 0:  # The square is free
                        self.moves.loc[row+row_dif,col+col_dif] = 1
                    elif colourarray.loc[row+row_dif,col+col_dif] == self.colour:
                        # Do nothing
                        t = 1
                    else:
                        self.moves.loc[row+row_dif,col+col_dif] = 1

    def validsquares(self):
        # This method packs the current valid moves into a simple
        squares_array = []
        for row in self.moves.index:
            for col in self.moves.columns:
                if self.moves.loc[row,col]:
                    squares_array.append(str(row)+str(col))
        return squares_array
