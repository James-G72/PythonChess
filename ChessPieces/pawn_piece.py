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
        # Returns the id that corresponds to the correct image
        return self.type+self.id

    def iterate(self):
        self.turns += 1

    def updatemoves(self,squarex,squarey,boardarray):
        print("update requested for "+str(self.type)+str(self.id))

    def validsquares(self):
        # This method packs the current valid moves into a simple
        squares_array = []
        for y in self.moves.index:
            for x in self.moves.columns:
                if self.moves.loc[x,y]:
                    squares_array.append(str(x)+str(y))
        return squares_array
