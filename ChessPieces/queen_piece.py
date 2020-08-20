import pandas as pd
import numpy as np

class Queen():
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

    def updatemoves(self,squarex,squarey,boardarray):
        t = 1

    def validsquares(self):
        # This method packs the current valid moves into a simple
        squares_array = []
        for y in self.moves.index:
            for x in self.moves.columns:
                if self.moves.loc[x,y]:
                    squares_array.append(str(x)+str(y))
        return squares_array