# This file represents a random computer for now which is just an excuse to have the game interact with something automated
import random

class Comp1:
    def __init__(self):
        self.colour_ref = ''
        self.colour = ''

    def getid(self):
        return "Random"

    def taketurn(self,boardarray,colourarray):
        # This allows the computer to be asked to take a turn
        # For now it remains random
        selected = False
        while not selected:
            rand_row = random.randint(0,7)
            rand_col = random.randint(0,7)
            if colourarray.loc[rand_row,rand_col] == self.colour:
                square1 = [rand_row,rand_col]
                possiblemoves = boardarray.loc[rand_row,rand_col].validsquares() # Request the possible moves
                if possiblemoves != []:
                    selection = random.randint(0,len(possiblemoves)-1)
                    square2 = [int(possiblemoves[selection][0]),int(possiblemoves[selection][1])]
                    selected = True

        return square1, square2