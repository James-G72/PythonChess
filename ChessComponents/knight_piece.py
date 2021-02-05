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
        """
        Returns the piece ID that was assigned on creation
        :return: Piece ID
        """
        return self.type+self.id

    def getcolour(self):
        """
        Returns the colour of the piece
        :return: Either "w" or "b"
        """
        return self.colour

    def iterate(self):
        """
        Logs the number of times that the piece has been moved
        :return: None
        """
        self.turns += 1

    def updatemoves(self,row,col,boardarray,colourarray):
        """
        The valid moves that the piece can make are stored internally. This function internally updates this tracker.
        :param row: The row in which the piece is located
        :param col: The column in which the piece is located
        :param boardarray: A dataframe that contains all of the pieces for reference
        :param colourarray: A simplified version of board array that shows what colour, if any, occupies each square
        :return: None
        """
        # The knight has the strangest moves but is quick to calculate
        # 8 pieces to check in a symmetric pattern
        self.moves = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7])
        for long in [-2,2]:
            for short in [-1,1]:
                checkrow = row + short
                checkcol = col + long
                if 0 <= checkrow <= 7 and 0 <= checkcol <= 7:
                    if colourarray.loc[checkrow,checkcol] == 0:  # The square is free
                        self.moves.loc[checkrow,checkcol] = 1
                    elif colourarray.loc[checkrow,checkcol] == self.colour:
                        free = False
                    else:
                        self.moves.loc[checkrow,checkcol] = 1
                checkrow = row + long
                checkcol = col + short
                if 0 <= checkrow <= 7 and 0 <= checkcol <= 7:
                    if colourarray.loc[checkrow,checkcol] == 0:  # The square is free
                        self.moves.loc[checkrow,checkcol] = 1
                    elif colourarray.loc[checkrow,checkcol] == self.colour:
                        free = False
                    else:
                        self.moves.loc[checkrow,checkcol] = 1

    def validsquares(self):
        """
        Places all valid moves into a list to be visualised.
        :return: List of all valid squares [[row1,col1],[row2,col2]]
        """
        squares_array = []
        for row in self.moves.index:
            for col in self.moves.columns:
                if self.moves.loc[row,col]:
                    squares_array.append(str(row)+str(col))
        return squares_array
