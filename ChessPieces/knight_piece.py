import pandas as pd
import numpy as np

class Knight():
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
        if self.colour == "w":
            self.moves.loc[5,col-1] = 1
            self.moves.loc[5,col+1] = 1
        else:
            self.moves.loc[2,col-1] = 1
            self.moves.loc[2,col+1] = 1

    def getid(self):
        # Returns the id that corresponds to the correct image
        return self.type+self.id

    def getcolour(self):
        return self.colour

    def iterate(self):
        self.turns += 1

    def updatemoves(self,row,col,boardarray,colourarray):
        t = 1

    def validsquares(self):
        # This method packs the current valid moves into a simple
        squares_array = []
        for row in self.moves.index:
            for col in self.moves.columns:
                if self.moves.loc[row,col]:
                    squares_array.append(str(row)+str(col))
        return squares_array
