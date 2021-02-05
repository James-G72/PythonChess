import pandas as pd
import numpy as np

class King():
    """
    The King class contains:
        getid()\n
        getcolour()\n
        iterate()\n
        updatemoves(row,col,boardarray,colourarray)\n
        validsquares()\n
        checkCheck(self,boardarray,row,col)\n
    """
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
        self.checkMate = False

        self.moves = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7])

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
        # The king is possibly the simplest piece to move
        # Castling hasn't been implemented yet
        self.moves = pd.DataFrame(np.zeros((8,8)),index=[0,1,2,3,4,5,6,7],columns=[0,1,2,3,4,5,6,7])
        for row_dif in [-1,0,1]:  # Going up from the row and then down
            for col_dif in [-1,0,1]:  # Going up from the column and then down
                comp = row_dif==0 and col_dif==0
                if 0 <= row+row_dif <= 7 and 0 <= col+col_dif <= 7 and not comp:
                    if colourarray.loc[row+row_dif,col+col_dif] == 0:  # The square is free
                        check, attacks = self.checkCheck(boardarray,row+row_dif,col+col_dif)
                        if not check:
                            self.moves.loc[row+row_dif,col+col_dif] = 1
                    elif colourarray.loc[row+row_dif,col+col_dif] == self.colour:
                        # Do nothing
                        t = 1
                    else:
                        self.moves.loc[row+row_dif,col+col_dif] = 1

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

    def checkCheck(self,boardarray,row,col):
        # This is unique to the king class and checks if this specific piece is in check
        # Once check has been established checkmate is easy to check for the king but the use of other pieces must be checked at the board level
        # All the pieces are checked to see if the king is a valid square for them. If it is then the king is in check.
        # This means that the same logic can be used to see if squares are invalid due to putting the king in check as it takes the boardarray and a row+column
        check = False
        attacks = [] # Indicates the squares that are attacking the given row/column
        for checkrow in range(0,8):
            for checkcol in range(0,8):
                if boardarray.loc[checkrow,checkcol] != 0:
                    if boardarray.loc[checkrow,checkcol].getcolour() != self.colour: # If the piece is an enemy
                        squares = boardarray.loc[checkrow,checkcol].validsquares()
                        for curr in squares:
                            if int(curr[0]) == row and int(curr[1]) == col:
                                check = True
                                attacks.append([row,col,checkrow,checkcol])
                                print(attacks)
        return check, attacks
