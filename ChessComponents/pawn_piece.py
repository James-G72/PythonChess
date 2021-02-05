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
            self.moves.loc[4:5,col] = 1
        else:
            self.moves.loc[2:3,col] = 1

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
        # row and col essentially tell the piece where it is
        self.moves = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7])
        reach = 1 # How far a pawn can reach
        if self.colour == "w":
            checkrow = row-reach
        else:
            checkrow = row+reach
        # There is an unsolved problem here whereby the pawn getting too close to the far end of the board throws an error
        if 7 >= checkrow >= 0:
            if colourarray.loc[checkrow,col] == 0:
                self.moves.loc[checkrow,col] = 1
                if self.turns == 0: # Then the pawn has moved and therefore cannot move twice
                    if self.colour == "w":
                        extrareach = checkrow-1
                    else:
                        extrareach = checkrow+1
                    if colourarray.loc[extrareach,col] == 0:
                        self.moves.loc[extrareach,col] = 1
                    else:
                        self.moves.loc[extrareach,col] = 0
            for checkcol in [col-1,col+1]:
                if checkcol >=0 and checkcol <=7:
                    if colourarray.loc[checkrow,checkcol] != self.colour and colourarray.loc[checkrow,checkcol] != 0:
                        self.moves.loc[checkrow,checkcol] = 1
                    else:
                        self.moves.loc[checkrow,checkcol] = 0
                    if colourarray.loc[checkrow,checkcol] != self.colour and colourarray.loc[checkrow,checkcol] != 0:
                        self.moves.loc[checkrow,checkcol] = 1
                    else:
                        self.moves.loc[checkrow,checkcol] = 0

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
