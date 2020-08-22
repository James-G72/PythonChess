import pandas as pd
import numpy as np

class Bishop():
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
        # The bishop is slightly awkward to do as it covers diagonal columns
        # This is pretty unoptimised at the moment but this probably won't interact with the algorithm so will only be triggered after each move
        self.moves = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7])
        for row_dif in [-1,1]:  # Going up from the row and then down
            for col_dif in [-1,1]:  # Going up from the column and then down
                checkrow = row + row_dif
                checkcol = col + col_dif
                free = True
                while 0 <= checkrow <= 7 and 0 <= checkcol <= 7 and free:
                    if colourarray.loc[checkrow,checkcol] == 0:  # The square is free
                        self.moves.loc[checkrow,checkcol] = 1
                    elif colourarray.loc[checkrow,checkcol] == self.colour:
                        free = False
                    else:
                        self.moves.loc[checkrow,checkcol] = 1
                        free = False
                    checkrow += row_dif
                    checkcol += col_dif

    def validsquares(self):
        # This method packs the current valid moves into a simple
        squares_array = []
        for row in self.moves.index:
            for col in self.moves.columns:
                if self.moves.loc[row,col]:
                    squares_array.append(str(row)+str(col))
        return squares_array